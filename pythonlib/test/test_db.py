import unittest

from sample_registry.db import CoreDb


class CoreDbTests(unittest.TestCase):
    def setUp(self):
        self.db = CoreDb(":memory:")
        self.db.create_tables()
        self.run = (
            u"2015-10-11", u"HiSeq", u"Nextera XT", 1,
            u"run_file.fastq", u"Bob's run",
            )
        self.run_acc = self.db.register_run(*self.run)
        self.samples = [
            (self.run_acc, "Sample1", "ABC"),
            (self.run_acc, "Sample2", "DEF"),
            (self.run_acc, "My.Sample3", "GHI"),
            ]
        self.single_sample = self.samples[0]
        self.annotations = {
            "SampleType": "Oral swab",
            "SubjectID": "Subj23",
            "study_group": "Healthy",
            "study_day": "1",
            }

    def test_register_run(self):        
        self.assertEqual(self.run_acc, 1)
        self.assertTrue(self.db.query_run_exists(self.run_acc))
        obs_run = self.db._query_run(self.run_acc)
        self.assertEqual(self.run, obs_run)

    def test_register_samples(self):
        # Here, accessions given by database cursor
        registered_accessions = self.db.register_samples(self.samples)
        self.assertEqual(registered_accessions, [1, 2, 3])
        # Double-check that we can actually find the samples in a query
        queried_accessions = self.db.query_sample_accessions(self.samples)
        self.assertEqual(queried_accessions, [1, 2, 3])        

    def test_register_annotations(self):
        first_sample = self.samples[0]
        sample_accessions = self.db.register_samples([first_sample])
        acc = sample_accessions[0]
        annotation_triples = [
            (acc, k, v) for k, v in self.annotations.items()]
        self.db.register_annotations(annotation_triples)
        obs_annotations = self.db.query_sample_annotations(acc)
        self.assertEqual(obs_annotations, self.annotations)

    def test_remove_annotations(self):
        sample_accessions = self.db.register_samples(self.samples)
        annotation_triples = []
        for acc in sample_accessions:
            for k, v in self.annotations.items():
                annotation_triples.append((acc, k, v))
        self.db.register_annotations(annotation_triples)
        self.db.remove_annotations(sample_accessions)
        for acc in sample_accessions:
            obs_annotations = self.db.query_sample_annotations(acc)
            self.assertEqual(obs_annotations, {})
 
    def test_collect_standard_annotations(self):
        a = [
            (1, "SampleType", "a"),
            (1, "HostSpecies", "b"),
            (2, "SubjectID", "c"),
            ]
        obs = CoreDb._collect_standard_annotations(a)
        self.assertEqual(obs, {1: ["a", None, "b"], 2: [None, "c", None]})


if __name__ == "__main__":
    unittest.main()
