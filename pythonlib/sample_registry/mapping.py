"""Read, validate, and write sample info tables"""

import string


class SampleTable(object):
    # Arguably the core fields should be in a different class, because
    # they really are of concern to the database and not the table of
    # samples.
    CORE_FIELDS = ("sample_name", "barcode_sequence")

    NAs = set([
        "", "0000-00-00", "null", "Null", "NA", "na", "none", "None",
    ])

    def __init__(self, recs):
        self.recs = list(recs)

    @property
    def core_info(self):
        for r in self.recs:
            yield tuple(r.get(f, "") for f in self.CORE_FIELDS)

    @property
    def annotations(self):
        for r in self.recs:
            annotation_keys = set(r.keys()) - set(self.CORE_FIELDS)
            yield [(k, r[k]) for k in annotation_keys]

    def validate(self):
        _validate(self.recs)

    def write(self, f):
        rows = _cast(self.recs, ["sample_name", "barcode_sequence"], [])
        for row in rows:
            f.write(u"\t".join(row))
            f.write(u"\n")

    @classmethod
    def load(cls, f):
        recs = list(cls._parse(f))
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
            yield dict([(k, v) for k, v in zip(keys, vals) if v not in cls.NAs])

    @classmethod
    def _tokenize(cls, line):
        """Tokenize a single line"""
        line = line.rstrip("\n\r")
        toks = line.split("\t")
        return [t.strip() for t in toks]


class QiimeSampleTable(SampleTable):
    # Tuples of (Qiime field, normal field, default value)
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


class NexteraSampleTable(SampleTable):
    FWD_INDEX_KEY = "barcode_index_fwd"
    REV_INDEX_KEY = "barcode_index_rev"

    def __init__(self, recs):
        super(NexteraSampleTable, self).__init__(recs)
        self.convert_barcodes()

    def convert_barcodes(self):
        barcodes = dict(line.split() for line in NEXTERA_BARCODES.splitlines())
        for r in self.recs:
            try:
                fwd_index = r[self.FWD_INDEX_KEY]
                fwd_barcode = barcodes[fwd_index]
                rev_index = r[self.REV_INDEX_KEY]
                rev_barcode = barcodes[rev_index]
                r["barcode_sequence"] = fwd_barcode + "-" + rev_barcode
            except KeyError as e:
                raise KeyError(
                    "Could not find DNA barcode sequence for this record:\n"
                    "%s\n%s" % (r, e)
                )


def _cast(records, left_cols, right_cols, missing="NA"):
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


ALLOWED_CHARS = {
    "sample_name": set("._-" + string.ascii_letters + string.digits),
    "barcode_sequence": set("AGCT"),
    "primer_sequence": set("AGCTRYMKSWHBVDN"),
    }


def _validate(recs):
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

NEXTERA_BARCODES = u"""\
N701	TAAGGCGA
N702	CGTACTAG
N703	AGGCAGAA
N704	TCCTGAGC
N705	GGACTCCT
N706	TAGGCATG
N707	CTCTCTAC
N708	CAGAGAGG
N709	GCTACGCT
N710	CGAGGCTG
N711	AAGAGGCA
N712	GTAGAGGA
N714	GCTCATGA
N715	ATCTCAGG
N716	ACTCGCTA
N718	GGAGCTAC
N719	GCGTAGTA
N720	CGGAGCCT
N721	TACGCTGC
N722	ATGCGCAG
N723	TAGCGCTC
N724	ACTGAGCG
N726	CCTAAGAC
N727	CGATCAGT
N728	TGCAGCTA
N729	TCGACGTC
S501	TAGATCGC
S502	CTCTCTAT
S503	TATCCTCT
S504	AGAGTAGA
S505	GTAAGGAG
S506	ACTGCATA
S507	AAGGAGTA
S508	CTAAGCCT
S510	CGTCTAAT
S511	TCTCTCCG
S513	TCGACTAG
S515	TTCTAGCT
S516	CCTAGAGT
S517	GCGTAAGA
S518	CTATTAAG
S520	AAGGCTAT
S521	GAGCCTTA
S522	TTATGCGA
"""
