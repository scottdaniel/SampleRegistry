from collections import namedtuple
import io
import unittest

from sample_registry import mapping 
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

    def test_create_qiime(self):
        f = io.StringIO()
        obs = mapping.create_qiime(f, self.run, self.samples, self.annotations)
        self.assertEqual(f.getvalue(), MAPPING_TEXT)

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
        self.assertEqual(sample_tup, ("S1", "GCCT"))
        self.assertEqual(list(sorted(annotation_tups)), [
            ("HostSpecies", "Human"),
            ("SubjectID", "Hu23"),
            ('primer_sequence', 'AGGCTT')])


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
