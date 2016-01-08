from collections import namedtuple
import io
import unittest

from sample_registry.mapping import (
    SampleTable, QiimeSampleTable, validate, create,
)
from sample_registry.models import Sample, Run


class FunctionTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(
            1, "2012-01-01", "GS-Junior", "Titanium",
            1, "file.sff", "Comment")
        self.samples = [
            Sample(21, "S1", "GCCT", self.run),
            Sample(22, "S2", "GCAT", self.run),
            ]
        self.annotations = [
            (21, "HostSpecies", "Human"),
            (21, "SubjectID", "Hu23"),
            (21, "primer_sequence", "AGGCTT"),
            (22, "primer_sequence", "AGGCTT"),
            ]
        self.qiime_recs = [
            {
                "SampleID": "S1",
                "BarcodeSequence": "GCCT",
                "LinkerPrimerSequence": "AGGCTT",
                "HostSpecies": "Human",
                "SubjectID": "Hu23",
                "Description": "PCMP000021",
                },
            {
                "SampleID": "S2",
                "BarcodeSequence": "GCAT",
                "LinkerPrimerSequence": "AGGCTT",
                "Description": "PCMP000022",
                },
            ]
        self.recs = [
            {
                "sample_name": "S1",
                "barcode_sequence": "GCCT",
                "primer_sequence": "AGGCTT",
                "HostSpecies": "Human",
                "SubjectID": "Hu23",
                },
            {
                "sample_name": "S2",
                "barcode_sequence": "GCAT",
                "primer_sequence": "AGGCTT",
                },
            ]

    def test_parse(self):
        input_file = io.StringIO(MAPPING_TEXT)
        t = SampleTable.load(input_file)
        self.assertEqual(t.recs, QIIME_RECS)

    def test_validate(self):
        self.assertEqual(validate(NORMAL_RECS), None)
        modified_recs = [r.copy() for r in NORMAL_RECS]
        modified_recs[1]["sample_name"] = "S1"
        self.assertRaises(ValueError, validate, modified_recs)


class QiimeSampleTableTests(unittest.TestCase):
    def test_convert_from_qiime(self):
        obs = QiimeSampleTable(QIIME_RECS)
        self.assertEqual(obs.recs, NORMAL_RECS)



NORMAL_RECS = [
    {
        "sample_name": "S1",
        "barcode_sequence": "GCCT",
        "primer_sequence": "AGGCTT",
        "HostSpecies": "Human",
        "SubjectID": "Hu23",
    },
    {
        "sample_name": "S2",
        "barcode_sequence": "GCAT",
        "primer_sequence": "AGGCTT",
    },
]

QIIME_RECS = [
    {
        "SampleID": "S1",
        "BarcodeSequence": "GCCT",
        "LinkerPrimerSequence": "AGGCTT",
        "HostSpecies": "Human",
        "SubjectID": "Hu23",
        "Description": "PCMP000021",
    },
    {
        "SampleID": "S2",
        "BarcodeSequence": "GCAT",
        "LinkerPrimerSequence": "AGGCTT",
        "Description": "PCMP000022",
    },
]


MAPPING_TEXT = u"""\
#SampleID	BarcodeSequence	LinkerPrimerSequence	HostSpecies	SubjectID	Description
#Comment
#Sequencing date: 2012-01-01
#Region: 1
#Platform: GS-Junior Titanium
#Run accession: PCMP000001
S1	GCCT	AGGCTT	Human	Hu23	PCMP000021
S2	GCAT	AGGCTT	NA	NA	PCMP000022
"""


if __name__ == '__main__':
    unittest.main()
