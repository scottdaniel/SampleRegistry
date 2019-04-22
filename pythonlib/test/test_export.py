import os
import unittest

from sample_registry.export import (
    IlluminaFastqFileSet, absolute_filepath, remount_filepath,
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
        
