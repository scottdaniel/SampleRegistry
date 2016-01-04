import io
import tempfile
import unittest

from sample_registry.db import CoreDb
from sample_registry.mapping import create
from sample_registry.register import (
    register_run, register_sample_annotations,
)


def temp_sample_file(samples):
    f = tempfile.NamedTemporaryFile(mode="wt")
    create(f, samples)
    f.seek(0)
    return f


class RegisterScriptTests(unittest.TestCase):
    def setUp(self):
        self.db = CoreDb(":memory:")
        self.db.create_tables()
        self.run_args = [
            "--file", "abc",
            "--lane", "1",
            "--date", "2008-09-21",
            "--type", "Illumina-MiSeq",
            "--kit", "Nextera XT",
            "--comment", "mdsnfa adsf",
        ]
        self.samples = [{
            "sample_name": "abc123",
            "barcode_sequence": "GGGCCT",
            "SampleType": "Oral swab",
            "bb": "cd e29",
        }]

    def test_rgister_run(self):
        out = io.StringIO()
        register_run(self.run_args, self.db, out)

        # Check that accession number is printed
        self.assertEqual(
            out.getvalue(),
            "Registered run 1 in the database\n"
        )

        # Check that attributes are saved in the database
        self.assertEqual(self.db._query_run(1), (
            u'2008-09-21', u'Illumina-MiSeq', u'Nextera XT', 1,
            u'abc', u'mdsnfa adsf'))

    def test_register_samples(self):
        register_run(self.run_args, self.db)
        out = io.StringIO()
        sample_file = temp_sample_file(self.samples)
        args = ["-r", "1", "-s", sample_file.name]
        register_sample_annotations(args, True, self.db, out)

        # Check that accession number is assigned
        self.assertEqual(
            self.db.query_sample_accessions([("1", "abc123", "GGGCCT")]),
            [1])

        # Check that annotations are saved to the database
        self.assertEqual(
            self.db.query_sample_annotations(1),
            {"SampleType": "Oral swab", "bb": "cd e29"})

    def test_register_annotations(self):
        register_run(self.run_args, self.db)
        sample_file = temp_sample_file(self.samples)
        args = ["-r", "1", "-s", sample_file.name]
        register_sample_annotations(args, True, self.db)

        # Update SampleType, add fg
        new_annotations = {"SampleType": "Feces", "fg": "hi5 34"}
        modified_samples = [x.copy() for x in self.samples]
        modified_samples[0].update(new_annotations)
        # Remove bb
        del modified_samples[0]["bb"]
        sample_file = temp_sample_file(modified_samples)
        args = ["-r", "1", "-s", sample_file.name]
        register_sample_annotations(args, False, self.db)

        self.assertEqual(
            self.db.query_sample_annotations(1), new_annotations)
