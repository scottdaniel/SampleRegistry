"""Script functions to regster new elements in the CORE database"""

import logging
import argparse
import os
import sys

from sample_registry import db, mapping, models


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CORE = db.CoreDb(THIS_DIR + "/../../website/core.db")


COMMON_DESC = """\
The sample table is a tab-separated values (TSV) file with one row for
each sample.  The field names are given on the first line. Comment
characters (#) are removed from the beginning of this line, if
present.  Subsequent lines of the file are expected to be comments
or values.  Comment lines must start with a '#' character.  Rows of
sample info may not contain blank entries; please use 'NA' if a
field does not apply to a sample.

The 'sample_name' field is exprected to be filled in for each sample.
Letters, numbers, dots, dashes, and underscores are allowed in
sample names.  No spaces are permitted.

The fields 'barcode_sequence', 'primer_sequence', and 'linker_sequence'
are also used to fill in the corresponding columns in the samples
table of the CORE registry database.  The combination of barcode and
primer sequences must be unique for each sample.  Barcode sequences
must be in upper case, unambiguous DNA characters (A, C, G, T).
Primer sequences may contain ambiguous DNA characters (R, Y, N,
etc.).  Linker sequences are not checked.
    
Additional fields are stored in the CORE registry database as sample
annotations.

For convenience, sample info may be provided in QIIME-compatible format.
In this case, the 'Description' field will be removed, and other
fields will be converted as follows: SampleID to sample_name,
BarcodeSequence to barcode_sequence, and LinkerPrimerSequence to
primer_sequence.
"""

SAMPLES_DESC = """\
Add new samples to the CORE database, with annotations.

""" + COMMON_DESC

ANNOTATIONS_DESC = """\
Replace annotations for samples in the CORE database.  Samples are
matched using info in the sample table (sample name, barcode, primer).

""" + COMMON_DESC

ANNOTATIONS_EPILOG = """\
**BEWARE USER** This script will replace all existing annotations with
those found in the provided file!  Make sure this is what you want, or
you will be restoring database tables with Time Machine, as you deserve.
You have been warned!!!
"""


def register_samples_script():
    return register_sample_annotations(None, True)


def register_annotations_script():
    return register_annotations_script(None, False)


def register_sample_annotations(argv=None, register_samples=False, coredb=None):
    if coredb is None:
        coredb = CORE

    if register_samples:
        p = argparse.ArgumentParser(description=SAMPLES_DESC)
    else:
        p = argparse.ArgumentParser(
            description=ANNOTATIONS_DESC, epilog=ANNOTATIONS_EPILOG)
    p.add_option(
        "-r", "--run_accession",
        type=int, required=True,
        help="Run accession")
    p.add_option(
        "-s", "--sample_info_file",
        type=argparse.FileType('r'), required=True,
        help="Sample table in TSV format")
    args = p.parse_args(argv)

    # Read sample table
    recs = list(mapping.parse(args.sample_info_file))
    if not recs:
        p.error("No records found.  Problem with windows line endings?")
    mapping.validate(recs)
    samples, annotations = zip(*list(mapping.split_annotations(recs)))

    # Check for run
    if not coredb.query_run_exists(opts.run_accession):
        raise ValueError("Run does not exist %s" % opts.run_accession)

    # Register and search for samples
    sample_args = [(opts.run_accession, n, b) for n, b in samples]
    if register_samples:
        coredb.register_samples(sample_args)
    accessions = coredb.query_sample_accessions(sample_args)
    unaccessioned = [s for a, s in zip(accessions, samples) if a is None]
    if any(unaccessioned):
        raise IOError("Not accessioned: %s" % unaccessioned)

    # Register annotations
    annotation_args = []
    for a, pairs in zip(accessions, annotations):
        for k, v in pairs:
            annotation_args.append((a, k, v))
    coredb.remove_annotations(accessions)
    coredb.register_annotations(annotation_args)


def register_run(argv=None, coredb=None, out=sys.stdout):
    if coredb is None:
        coredb = CORE

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
