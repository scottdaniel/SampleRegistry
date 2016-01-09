"""Add samples and runs to the registry"""

import argparse
import os
import sys

from sample_registry.db import CoreDb
from sample_registry.mapping import SampleTable


__THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_DATABASE = CoreDb(__THIS_DIR + "/../../website/core.db")


SAMPLES_DESC = """\
Add new samples to the registry, with annotations.
"""

ANNOTATIONS_DESC = """\
Replace annotations for samples in the registry.  Samples are matched
using the sample ID and barcode sequence.
"""

ANNOTATIONS_EPILOG = """\
**BEWARE USER** This script will replace all existing annotations with
those found in the provided file!  Make sure this is what you want, or
you will be restoring database tables from backup files, as you deserve.
You have been warned!!!
"""

SAMPLE_TABLE_HELP = """\
Sample table in tab-separated values (TSV) format.  Field names are
listed in the first line.  If the first line begins with '#', the
character is ignored.  Other lines beginning with '#' are interpreted
as comments.
"""


def register_samples():
    return register_sample_annotations(None, True)


def register_annotations():
    return register_sample_annotations(None, False)


def register_sample_annotations(
        argv=None, register_samples=False, coredb=REGISTRY_DATABASE,
        out=sys.stdout):

    if register_samples:
        p = argparse.ArgumentParser(description=SAMPLES_DESC)
    else:
        p = argparse.ArgumentParser(
            description=ANNOTATIONS_DESC, epilog=ANNOTATIONS_EPILOG)

    p.add_argument(
        "run_accession", type=int,
        help="Run accession number")
    p.add_argument(
        "sample_table", type=argparse.FileType('r'),
        help=SAMPLE_TABLE_HELP)
    args = p.parse_args(argv)

    registry = SampleRegistry(coredb)
    sample_table = SampleTable.load(args.sample_table)
    sample_table.look_up_nextera_barcodes()
    sample_table.validate()

    registry.check_run_accession(args.run_accession)
    if register_samples:
        registry.register_samples(args.run_accession, sample_table)
    registry.register_annotations(args.run_accession, sample_table)


def register_run(argv=None, coredb=REGISTRY_DATABASE, out=sys.stdout):
    machines = [
        "Illumina-MiSeq",
        "Illumina-HiSeq",
    ]
    kits = [
        "Nextera XT"
    ]

    p = argparse.ArgumentParser(
        description="Register a new run in the CORE database.")
    p.add_argument(
        "--file", required=True,
        help="Resource filepath (not checked for validity)")
    p.add_argument(
        "--date", required=True,
        help="Run date (YYYY-MM-DD)")
    p.add_argument(
        "--comment", required=True,
        help="Comment (free text)")
    p.add_argument(
        "--type", default="Immulina-MiSeq", choices=machines,
        help="Machine type")
    p.add_argument(
        "--kit", default="Nextera XT", choices=kits,
        help="Machine kit")
    p.add_argument("--lane", default="1",
        help="Lane number")
    args = p.parse_args(argv)

    acc = coredb.register_run(
        args.date, args.type, args.kit, args.lane, args.file, args.comment)
    out.write(u"Registered run %s in the database\n" % acc)


class SampleRegistry(object):
    def __init__(self, registry_db):
        self.db = registry_db

    def check_run_accession(self, acc):
        if not self.db.query_run_exists(acc):
            raise ValueError("Run does not exist %s" % acc)

    def register_samples(self, run_accession, sample_table):
        args = [(run_accession, n, b) for n, b in sample_table.core_info]
        self.db.register_samples(args)

    def register_annotations(self, run_accession, sample_table):
        accessions = self._get_sample_accessions(run_accession, sample_table)
        annotation_args = []
        for a, pairs in zip(accessions, sample_table.annotations):
            for k, v in pairs:
                annotation_args.append((a, k, v))
        self.db.remove_annotations(accessions)
        self.db.register_annotations(annotation_args)

    def _get_sample_accessions(self, run_accession, sample_table):
        args = [(run_accession, n, b) for n, b in sample_table.core_info]
        accessions = self.db.query_sample_accessions(args)
        unaccessioned_recs = []
        for accession, rec in zip(accessions, sample_table.recs):
            if accession is None:
                unaccessioned_recs.append(rec)
        if unaccessioned_recs:
            raise IOError("Not accessioned: %s" % unaccessioned_recs)
        return accessions
