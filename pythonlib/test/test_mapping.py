from collections import namedtuple
import io
import unittest

from sample_registry.mapping import (
    SampleTable, QiimeSampleTable,
)


class FunctionTests(unittest.TestCase):
    def test_write(self):
        t = SampleTable(NORMAL_RECS)
        output_file = io.StringIO()
        t.write(output_file)
        self.assertEqual(output_file.getvalue(), NORMAL_TSV)

    def test_parse(self):
        input_file = io.StringIO(NORMAL_TSV)
        t = SampleTable.load(input_file)
        self.assertEqual(t.recs, NORMAL_RECS)

    def test_validate(self):
        t = SampleTable(NORMAL_RECS)
        self.assertEqual(t.validate(), None)

    def test_validate_with_duplicated_sample_name(self):
        modified_recs = [r.copy() for r in NORMAL_RECS]
        modified_recs[1]["sample_name"] = "S1"
        t = SampleTable(modified_recs)
        self.assertRaises(ValueError, t.validate)


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


NORMAL_TSV = u"""\
sample_name	barcode_sequence	HostSpecies	SubjectID	primer_sequence
S1	GCCT	Human	Hu23	AGGCTT
S2	GCAT	NA	NA	AGGCTT
"""


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


if __name__ == '__main__':
    unittest.main()
