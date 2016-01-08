from collections import namedtuple
import io
import unittest

from sample_registry.mapping import (
    SampleTable, QiimeSampleTable, NexteraSampleTable,
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


class NexteraSampleTableTests(unittest.TestCase):
    def test_real_table(self):
        input_file = io.StringIO(NEXTERA_TSV)
        t = NexteraSampleTable.load(input_file)
        self.assertEqual(t.recs[1]["barcode_sequence"], u"ACTCGCTA-TATCCTCT")


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


NEXTERA_TSV = u"""\
SampleID	external_id_tube	SampleType	SubjectID	HostSpecies	host_strain	study_day	study_group	SL_or_LL	study_sample	dna_location	dna_concentration_ng/ul	date_extracted	index_set	avg_frag_size_bp	FragA_nM	PG_lib_conc	barcode_index_fwd	barcode_index_rev	flow_cell_lane	flow_cell_id	run_start_date
HC.1.1.0.NA.1	1	Feces	1	Rat	sprague.dawley	0	HC	NA	1	original plate	36.73	20151203	B	252	13.675	3.42466	N716	S502	"5,6,7,8"	C8DEKANXX	20151209
HC.2.2.0.NA.1	2	Feces	2	Rat	sprague.dawley	0	HC	NA	1	original plate	0.97	20151203	B	213	5.33	0.67984	N716	S503	"5,6,7,8"	C8DEKANXX	20151209
HC.3.3.0.NA.1	3	Feces	3	Rat	sprague.dawley	0	HC	NA	1	original plate	0.84	20151203	B	327	8.035	1.41526	N716	S505	"5,6,7,8"	C8DEKANXX	20151209
"""


if __name__ == '__main__':
    unittest.main()
