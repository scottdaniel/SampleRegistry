"""Parse, create, and validate QIIME-style mapping files."""

import io
import string

NAs = set([
    "", "0000-00-00", "null", "Null", "NA", "na", "none", "None",
    ])


ALLOWED_CHARS = {
    "sample_name": set("._-" + string.ascii_letters + string.digits),
    "barcode_sequence": set("AGCT"),
    "primer_sequence": set("AGCTRYMKSWHBVDN"),
    }






class SampleTable(object):
    CORE_FIELDS = ("sample_name", "barcode_sequence")
    def __init__(self, recs):
        self.recs = list(recs)

    def validate(self):
        validate(self.recs)

    @classmethod
    def load(cls, f):
        recs = list(cls.parse(f))
        if not recs:
            raise ValueError(
                "No records found in sample info file. "
                "Problem with windows line endings?")
        return cls(recs)

    @classmethod
    def _parse(cls, f):
        """Parse mapping file, return each record as a dict."""
        header = next(f).lstrip("#")
        keys = cls._tokenize(header)
        assert(all(keys)) # No blank fields in header
        for line in f:
            if line.startswith("#"):
                continue
            if not line.strip():
                continue
            vals = cls._tokenize(line)
            yield dict([(k, v) for k, v in zip(keys, vals) if v not in NAs])

    @classmethod
    def _tokenize(cls, line):
        """Tokenize a single line"""
        line = line.rstrip("\n\r")
        toks = line.split("\t")
        return [t.strip() for t in toks]

    @property
    def core_info(self):
        for r in self.recs:
            yield tuple(r.get(f, "") for f in self.CORE_FIELDS)

    @property
    def annotations(self):
        for r in self.recs:
            annotation_keys = set(r.keys()) - set(self.CORE_FIELDS)
            yield [(k, r[k]) for k in annotation_keys]


class QiimeSampleTable(SampleTable):
    QIIME_FIELDS = (
        ("SampleID", "sample_name", None),
        ("BarcodeSequence", "barcode_sequence", None),
        ("LinkerPrimerSequence", "primer_sequence", ""),
        ("Description", "accession", None),
    )

    def __init__(self, recs):
        super(QiimeSampleTable, self).__init__(recs)
        self.convert()

    def convert(self):
        """Convert records from a QIIME mapping file to registry format."""
        for r in self.recs:
            # Description column is often filled in with junk, and we
            # fill it in with new values when exporting.  Remove it if
            # present.
            if "Description" in r:
                del r["Description"]
            for qiime_field, core_field, default_val in self.QIIME_FIELDS:
                if core_field in r:
                    raise ValueError(
                        "Trying to convert from QIIME format mapping, but core "
                        "field %s is already present and filled in.")
                qiime_val = r.pop(qiime_field, None)
                if qiime_val is not None:
                    r[core_field] = qiime_val


def create(f, samples):
    rows = cast(samples, ["sample_name", "barcode_sequence"], [])
    for row in rows:
        f.write(u"\t".join(row))
        f.write(u"\n")


def cast(records, left_cols, right_cols, missing="NA"):
    records = list(records)
    all_cols = set(left_cols + right_cols)
    for r in records:
        for key in sorted(r.keys()):
            if key not in all_cols:
                left_cols.append(key)
                all_cols.add(key)

    header = left_cols + right_cols
    yield header

    for r in records:
        row = [missing for _ in header]
        for key, val in r.items():
            idx = header.index(key)
            row[idx] = val
        yield row


def _modify_fields_for_qiime(sample):
    for qiime_col, orig_col, default_val in QiimeSampleTable.QIIME_FIELDS:
        if orig_col in sample:
            sample[qiime_col] = sample[orig_col]
            del sample[orig_col]
        if (qiime_col not in sample) and (default_val is not None):
            sample[qiime_col] = default_val
    return sample


def _integrate_eav(samples, annotations):
    sample_accessions = [(s.accession, s.as_dict()) for s in samples]
    samples_by_accession = dict(sample_accessions)
    for acc, key, val in annotations:
        s = samples_by_accession.get(acc)
        if s is not None:
            s[key] = val
    return [s for _, s in sample_accessions]


def create_qiime(f, run, samples, annotations):
    """Create a QIIME mapping file."""
    samples = _integrate_eav(samples, annotations)
    samples = [_modify_fields_for_qiime(s) for s in samples]
    qiime_left = ["SampleID", "BarcodeSequence", "LinkerPrimerSequence"]
    qiime_right = ["Description"]
    rows = cast(samples, qiime_left, qiime_right)

    header = next(rows)
    f.write(u"#")
    f.write(u"\t".join(header))
    f.write(u"\n")

    f.write(u"#%s\n" % run.comment)
    f.write(u"#Sequencing date: %s\n" % run.date)
    f.write(u"#Region: %s\n" % run.region)
    f.write(u"#Platform: %s\n" % run.platform)
    f.write(u"#Run accession: %s\n" % run.formatted_accession)

    for row in rows:
        f.write(u"\t".join(row))
        f.write(u"\n")






def validate(recs):
    """Ensure records are valid.

    Does not return a value, but raises an exception on an invalid record.
    """
    sample_names = set()
    barcodes = set()

    for r in recs:
        for key, char_set in ALLOWED_CHARS.items():
            if key in r:
                val = r[key]
                if not all(char in char_set for char in val):
                    raise ValueError("Illegal characters in %s: %s" % (key, r))

        name = r.get("sample_name")
        if name is None:
            raise ValueError("No sample_name: %s" % r)
        if name in sample_names:
            raise ValueError("Duplicate sample_name: %s" % r)
        sample_names.add(name)

        barcode = r.get("barcode_sequence", "")
        if barcode in barcodes:
            raise ValueError("Duplicate barcode: %s" % r)
        barcodes.add(barcode)
