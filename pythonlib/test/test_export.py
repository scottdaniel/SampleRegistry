import gzip
import os
import shutil
import tempfile
import unittest

from sample_registry.export import (
    IlluminaFastqFileSet, export_samples,
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


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp_input_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_input_dir)
        shutil.rmtree(self.temp_output_dir)

    def test_export_samples(self):
        run_info = {
            "run": {"data_uri": "data_R1.fastq.gz"},
            "samples": [
                {"sample_name": "SampleA", "barcode_sequence": "AAAGGG"}]
        }

        # CCCTTT is the reverse complement of AAAGGG
        header = "@HWI-D00727:9:C6JHHANXX:8:1101:1361:2237 1:N:0:CCCTTT"
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
        export_samples(args, run_info)

        # Ensure barcodes file written
        with open(os.path.join(self.temp_output_dir, "barcodes.txt")) as f:
            self.assertEqual(f.read(), "SampleA\tAAAGGG\n")

        # Ensure script written
        with open(os.path.join(self.temp_output_dir, "run_dnabc.sh")) as f:
            next(f) # skip shebang line
            self.assertTrue(next(f).startswith("dnabc.py --barcode-file "))
