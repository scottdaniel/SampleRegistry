import gzip
import os.path
import shutil
import tempfile
import unittest

from sample_registry.models import (
    Sample, Run,
    )


class SampleTests(unittest.TestCase):
    def test_init(self):
        s = Sample(1, "a", "agct", 123)
        self.assertEqual(s.barcode, "AGCT")


class RunTests(unittest.TestCase):
    def test_file_format(self):
        def R(fp):
            return Run(123, None, None, None, None, fp, None)
        self.assertEqual(R("file/").file_format, "FASTQ")
        self.assertEqual(R("file/").file_format, "FASTQ")
        self.assertEqual(R("file.fastq.gz").file_format, "FASTQ")
        self.assertEqual(R("file.fna").file_format, "FASTA")
        self.assertEqual(R("file.fasta").file_format, "FASTA")
        self.assertEqual(R("file.sff").file_format, "SFF")


if __name__ == "__main__":
    unittest.main()
