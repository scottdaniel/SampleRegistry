"""Model classes, closely tied to database."""
import os.path

from sample_registry.util import deambiguate


class Sample(object):
    def __init__(self, accession, name, barcode, primer, run):
        self.accession = accession
        self.name = name

        self.barcode = barcode
        if self.barcode is not None:
            self.barcode = self.barcode.upper()

        self.primer = primer
        if self.primer is not None:
            self.primer = self.primer.upper()

        self.run = run

    @property
    def formatted_accession(self):
        return "BLS%06d" % self.accession

    @property
    def prefixes(self):
        """Returns all non-degenerate versions of a given primer sequence """
        return [self.barcode + p for p in deambiguate(self.primer)]


class Run(object):
    def __init__(self, accession, date, mach_type, mach_kit, region, fp, comment):
        self.accession = accession  # Must be a number
        self.date = date
        self.machine_type = mach_type
        self.machine_kit = mach_kit
        self.region = region
        self.fp = fp
        self.comment = comment

    @property
    def file_format(self):
        """Infer the input file format.

        Unlike the methods elsewhere, this does not check that the file
        exists.
        """
        fp = self.fp
        if fp.endswith(".gz"):
            fp = fp[:-3]
        _, ext = os.path.splitext(fp)
        ext = ext.upper()[1:] # Remove leading dot and make ALL CAPS

        # The folder name is registered for Illumina runs where
        # samples are pre-split.  There should be no other type of run
        # without a file extension.  Therefore, if we see a blank file
        # extension, we assume that the filepath is a folder
        # containing FASTQ files.
        if ext == "":
            return "FASTQ"
        # FASTA files can also be named with .fna
        if ext == "FNA":
            return "FASTA"
        return ext
    
    @property
    def formatted_accession(self):
        return "BLR%06d" % self.accession

    @property
    def platform(self):
        return "%s %s" % (self.machine_type, self.machine_kit)

    @property
    def prefix(self):
        if self.fp.endswith(".sff"):
            fn = os.path.basename(self.fp)
            return fn[:-6] # runprefix01.sff, remove 6 chars from end
        return ""


