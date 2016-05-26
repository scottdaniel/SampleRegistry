import io
import tempfile
import unittest

from sample_registry.db import CoreDb
from sample_registry.mapping import SampleTable
from sample_registry.register import (
    register_run, register_sample_annotations,
    get_illumina_info, unregister_samples,
)


def temp_sample_file(samples):
    f = tempfile.NamedTemporaryFile(mode="wt")
    t = SampleTable(samples)
    t.write(f)
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
            "SampleID": "abc123",
            "BarcodeSequence": "GGGCCT",
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
        args = ["1", sample_file.name]
        register_sample_annotations(args, True, self.db, out)

        # Check that accession number is assigned
        obs_accessions = self.db.query_barcoded_sample_accessions(
            1, [("abc123", "GGGCCT")])
        self.assertEqual(obs_accessions, [1])

        # Check that annotations are saved to the database
        self.assertEqual(
            self.db.query_sample_annotations(1),
            {"SampleType": "Oral swab", "bb": "cd e29"})

    def test_register_annotations(self):
        register_run(self.run_args, self.db)
        sample_file = temp_sample_file(self.samples)
        args = [ "1", sample_file.name]
        register_sample_annotations(args, True, self.db)

        # Update SampleType, add fg
        new_annotations = {"SampleType": "Feces", "fg": "hi5 34"}
        modified_samples = [x.copy() for x in self.samples]
        modified_samples[0].update(new_annotations)
        # Remove bb
        del modified_samples[0]["bb"]
        sample_file = temp_sample_file(modified_samples)
        args = ["1", sample_file.name]
        register_sample_annotations(args, False, self.db)

        self.assertEqual(
            self.db.query_sample_annotations(1), new_annotations)

    def test_unregister_samples(self):
        register_run(self.run_args, self.db)
        out = io.StringIO()
        sample_file = temp_sample_file(self.samples)
        args = ["1", sample_file.name]
        register_sample_annotations(args, True, self.db, out)

        unregister_samples(["1"], self.db)
        self.assertEqual(self.db._query_nonstandard_annotations(1), {})
        self.assertEqual(self.db.query_sample_accessions(1), [])

    def test_get_illumina_info(self):
        r1 = io.StringIO(R1_FASTQ)
        run_info = get_illumina_info(r1)
        expected = {
            "instrument": "D00728",
            "run_number": "20",
            "flowcell_id": "C8DEKANXX",
            "lane": "1",
            "read": "1",
            "is_filtered": "N",
            "control_num": "0",
            "barcode_seq": "GTAGAGGA+AAGGAGTA",
        }
        self.assertEqual(run_info, expected)

R1_FASTQ = u"""\
@D00728:20:C8DEKANXX:1:1107:1197:2118 1:N:0:GTAGAGGA+AAGGAGTA
NATATCAGCTGGTATGATTTCACAAAAGAAATCTTCCGTCAGGCCGCTGCCATGGGACACCCGGAATATCTCCCGGAAAACATGACAGTCAACTCCGTCACAACTGCAGAGTATGGCGCTTCCAAA
+
#<<>0EFGCGGEGGGGFGGGGGGGGGGGGGGGGGGGGGGGG>EBGGGGG@GGGGGEGGGG@GGGG<GGG@GCGBGG/CGGGGGG>GGGGFGEGGDGGEGGGGGGGGGG=0@CBD=CDG<>8@GGGG
@D00728:20:C8DEKANXX:1:1107:1160:2123 1:N:0:TCCTGAGC+CTACGCCT
NTATTAACTCGGCTTTATCAAATTCTTTCTTATTCTTCATCACAGCTCCAACAAATCGCTCTATCATTGTTTTGTCTAATTCTATTTCTCTACCCAAATTAAATAAACCAACAGCTGTCTCTTATA
+
#=<<>>1FEGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGFFGGGGGGGGGGBGGGGGG>GGGGG>GGFGGGGGGGGGGGF
@D00728:20:C8DEKANXX:1:1107:1236:2146 1:N:0:ATCTCAGG+TATCCTCT
CGTTGATTCTTAGATGCACATGTAAGATACCACAGATACTTTTTAGATTATTCCTGTCTCTTATACACATCTCCGAGCCCACGAGACATCGCAGGTTCTCGTATGCCGTCTTCTGCTTGAAAAAAA
+
@BBBC>GGGFGEF@EFGGGFGGGGGGFDGGGGG@GCG@GEFFGGGFFGDGGGGFGGGGEGGG>FGDGGGGCFGGGGGGG@>GG/E=ECFG/=/=C00?<EGG.FGGGGGGGGGGGGG0<0:6D-,,
@D00728:20:C8DEKANXX:1:1107:1048:2153 1:N:0:ATCTCAGG+GTAAGNGG
GTTGAAATCGTTGCCATTGATTGTTCCACTGGTTTTGTAACTGTCGTTTCCACAGTCTCCGGAGCTGTCTCTTATACACATCTCCGAGCCCACGAGACATCTCAGGATCTCGTATGCCGTCTTCTG
+
3=@BBGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGFGGGGGGGGGGGGG@GFGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG<>CDFGGGGGGGG0CFFGG<GG=CGGDGGGG.
"""

R2_FASTQ = u"""\
@D00728:20:C8DEKANXX:1:1107:1197:2118 2:N:0:GTAGAGGA+AAGGAGTA
TACCTTATGTATTCTGCTTCAATCCGGCAATGCTGCTGATCGATACCACACCACTTAAGGTTGTTCAGATCTTTATCACCTCACTGATTGGTGTGTTTGGATTGTCCTCCTCACTGGAAGGCTTCT
+
BBBCBGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGFGGCGGGGGGEGGGGGGGGFGGFGGGBFFBFGGGGGGGGGGGGGBCF@F-8FFDGGGG/
@D00728:20:C8DEKANXX:1:1107:1160:2123 2:N:0:TCCTGAGC+CTACGCCT
CTGTTGGTTTATTTAATTTGGGTAGAGAAATAGAATTAGACAAAACAATGATAGAGCGATTTGTTGGAGCTGTGATGAAGAATAAGAAAGAATTTGATAAAGCCGAGTTAATATCTGTCTCTTATA
+
CCCCCGGGGGGGGGGGFGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGFGGGGGGB@G:FGCGGGGEGGGCEECCG/
@D00728:20:C8DEKANXX:1:1107:1236:2146 2:N:0:ATCTCAGG+TATCCTCT
GAATAATCTAAAAAGTATCTGTGGTATCTTACATGTGCATCTAAGAATCAACGCTGTCTCTTATACACATCTGACGCTGCCGACGAAGAGGATAGTGTAGATCTCGGTGGTCGCCGTATCATTAAA
+
CCCCCGGGGGGGGEFEFGGGFFGGGGFGFGGGGGFDGGGGGFBCF1C@FGGGFGGGFFGEFDGGGGGGGCGGGFGGGGG<GG/EC9EG>GGG>?CFFDFGG/D@>FG>FG5FG@DG,,--EE.BG.
@D00728:20:C8DEKANXX:1:1107:1048:2153 2:N:0:ATCTCAGG+GTAAGNGG
NTNCGGAGACTGTGGAAACGACAGTTACAAAACCAGTGGAACAATCAATGGCAACGATTTCAAACTGTCTCTTATACACATCTGACGCTGCCGACGACTCCTTACGTGTAGATCTCGGTGGTCGCC
+
#=#==FGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGFGGGGGGGGGGGGGGGGGGGGFGGGBGGBGGBGGGGEGD:
"""
