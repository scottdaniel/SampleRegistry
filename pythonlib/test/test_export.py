import gzip
import os
import shutil
import tempfile
import unittest

from sample_registry.export import (
    IlluminaFastqFileSet, absolute_filepath, remount_filepath, export_samples,
)

class IlluminaRunFileTests(unittest.TestCase):
    def test_filepath(self):
        fastq_dir = "/mnt/data/161222_M04734_0017_000000000-AVB6Y"
        r1_fname = "Undetermined_S0_L001_R1_001.fastq.gz"
        fs = IlluminaFastqFileSet(os.path.join(fastq_dir, r1_fname))
        self.assertEqual(fs.fastq_dir, fastq_dir)
        self.assertEqual(
            fs.r1_filepath,
            os.path.join(fastq_dir, "Undetermined_S0_L001_R1_001.fastq.gz"))
        self.assertEqual(
            fs.r2_filepath,
            os.path.join(fastq_dir, "Undetermined_S0_L001_R2_001.fastq.gz"))
        self.assertEqual(
            fs.i1_filepath,
            os.path.join(fastq_dir, "Undetermined_S0_L001_I1_001.fastq.gz"))
        self.assertEqual(
            fs.i2_filepath,
            os.path.join(fastq_dir, "Undetermined_S0_L001_I2_001.fastq.gz"))


class FilePathTests(unittest.TestCase):
    def test_absolute_filepath(self):
        self.assertEqual(absolute_filepath("/hello/there"), "/hello/there")

    def test_default_base_dir(self):
        self.assertEqual(absolute_filepath("hello/there"), "/hello/there")

    def test_base_dir_used_for_relative_fp(self):
        self.assertEqual(absolute_filepath("a/b.c", base_dir="/d/e"), "/d/e/a/b.c")

    def test_base_dir_not_used_for_absolute_fp(self):
        self.assertEqual(absolute_filepath("/a/b.c", base_dir="/d/e"), "/a/b.c")

    def test_local_mount(self):
        self.assertEqual(
            remount_filepath("/a/b/c/d.e", remote_mnt="/a/b", local_mnt="/f/g"),
            "/f/g/c/d.e")

    def test_invalid_mount_point(self):
        self.assertRaises(
            ValueError, remount_filepath, "/a/b/c.d",
            remote_mnt="/e/f", local_mnt="/g/h")

class MockDb:
    def _query_run(self, acc):
        return (
            "2015-10-11", "HiSeq", "Nextera XT", acc,
            "data_R1.fastq.gz", "Bob's run")

    def query_sample_barcodes(self, acc):
        return [("SampleA", "AAATTT")]


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp_input_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_input_dir)
        shutil.rmtree(self.temp_output_dir)

    def test_main(self):
        header = "@HWI-D00727:9:C6JHHANXX:8:1101:1361:2237 1:N:0:AAATTT"
        seq_fwd = "CGTGCGATGCTAGCTAGCGATTGC"
        seq_rev = "CGATCGACTGCTACGATCGACTAC"
        qual = "#=<BBGGGGGGGGGGGGGGGGGGG"

        fwd_filename = "data_R1.fastq.gz"
        fwd_fp = os.path.join(self.temp_input_dir, fwd_filename)
        with gzip.open(fwd_fp, "wt") as f:
            f.write("{0}\n{1}\n+\n{2}\n".format(header, seq_fwd, qual))

        rev_filename = "data_R2.fastq.gz"
        rev_fp = os.path.join(self.temp_input_dir, rev_filename)
        with gzip.open(rev_fp, "wt") as f:
            f.write("{0}\n{1}\n+\n{2}\n".format(header, seq_rev, qual))

        args = [
            "1", "--base-dir", self.temp_input_dir, "--output-dir",
            self.temp_output_dir]
        export_samples(args, db=MockDb())

        self.assertEqual(
            set(os.listdir(self.temp_output_dir)),
            set(("SampleA_R1.fastq", "SampleA_R2.fastq")))

        with open(os.path.join(self.temp_output_dir, "SampleA_R1.fastq")) as f:
            f1 = next(f)
            self.assertEqual(f1, header + "\n")
            f2 = next(f)
            self.assertEqual(f2, seq_fwd + "\n")
            f3 = next(f)
            self.assertEqual(f3, "+\n")
            f4 = next(f)
            self.assertEqual(f4, qual + "\n")
