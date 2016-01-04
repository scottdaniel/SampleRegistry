import io
import unittest

from sample_registry.db import CoreDb
from sample_registry.register import register_run

class RegisterRunTests(unittest.TestCase):
    def setUp(self):
        self.db = CoreDb(":memory:")
        self.db.create_tables()

    def test_rgister_run(self):
        args = [
            "--file", "abc",
            "--lane", "1",
            "--date", "2008-09-21",
            "--type", "Illumina-MiSeq",
            "--kit", "Nextera XT",
            "--comment", "mdsnfa adsf",
        ]
        out = io.StringIO()
        register_run(args, self.db, out)
        self.assertEqual(
            out.getvalue(),
            "Registered run 1 in CORE database\n"
        )
