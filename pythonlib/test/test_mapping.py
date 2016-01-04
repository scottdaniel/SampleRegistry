from collections import namedtuple
import unittest

from sample_registry import mapping 
from sample_registry.models import Sample, Run


class FunctionTests(unittest.TestCase):
    def setUp(self):
        self.run = Run(
            1, "2012-01-01", "GS-Junior", "Titanium",
            1, "file.sff", "Comment")
        self.samples = [
            Sample(21, "S1", "GCCT", "AGGCTT", self.run),
            Sample(22, "S2", "GCAT", "AGGCTT", self.run),
            ]
        self.annotations = [
            (21, "HostSpecies", "Human"),
            (21, "SubjectID", "Hu23"),
            ]
        self.qiime_recs = [
            {
                "SampleID": "S1",
                "BarcodeSequence": "GCCT",
                "LinkerPrimerSequence": "AGGCTT",
                "HostSpecies": "Human",
                "SubjectID": "Hu23",
                "Description": "BLS000021",
                },
            {
                "SampleID": "S2",
                "BarcodeSequence": "GCAT",
                "LinkerPrimerSequence": "AGGCTT",
                "Description": "BLS000022",
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

    def test_cast(self):
        obs_fields, obs_rows = mapping._cast(self.samples, self.annotations)
        self.assertEqual(obs_fields, ["HostSpecies", "SubjectID"])
        self.assertEqual(len(obs_rows), 2)
        self.assertEqual(obs_rows[0], ["Human", "Hu23"])
        self.assertEqual(obs_rows[1], ["NA", "NA"])

    def test_create(self):
        obs = mapping.create(self.run, self.samples, self.annotations)
        self.assertEqual(obs, MAPPING_TEXT)

    def test_parse(self):
        input_file = iter(MAPPING_TEXT.splitlines())
        rows = mapping.parse(input_file)
        self.assertEqual(list(rows), self.qiime_recs)

    def test_convert_from_qiime(self):
        obs = mapping.convert_from_qiime(self.qiime_recs)
        self.assertEqual(list(obs), self.recs)

    def test_validate(self):
        self.assertEqual(mapping.validate(self.recs), None)

        self.recs[1]["sample_name"] = "S1"
        self.assertRaises(ValueError, mapping.validate, self.recs)

    def test_split_annotations(self):
        split_recs = mapping.split_annotations(self.recs)
        sample_tup, annotation_tups = next(split_recs)
        self.assertEqual(sample_tup, ("S1", "GCCT", "AGGCTT"))
        self.assertEqual(
            list(sorted(annotation_tups)), 
            [("HostSpecies", "Human"), ("SubjectID", "Hu23")],
            )


MAPPING_TEXT = u"""\
#SampleID	BarcodeSequence	LinkerPrimerSequence	HostSpecies	SubjectID	Description
#Comment
#Sequencing date: 2012-01-01
#Region: 1
#Platform: GS-Junior Titanium
#Bushman lab run accession: BLR000001
S1	GCCT	AGGCTT	Human	Hu23	BLS000021
S2	GCAT	AGGCTT	NA	NA	BLS000022
"""


if __name__ == '__main__':
    unittest.main()
