import argparse
import gzip
import os


from .db import RegistryDatabase
from .register import REGISTRY_DATABASE
from dnabclib.assigner import BarcodeAssigner
from dnabclib.sample import Sample
from dnabclib.seqfile import SequenceFile
from dnabclib.writer import PairedFastqWriter


def absolute_filepath(fp, base_dir="/"):
    if not os.path.isabs(fp):
        fp = os.path.join(base_dir, fp)
    return fp


def remount_filepath(fp, remote_mnt, local_mnt):
    fp = os.path.normpath(fp)
    remote_mnt = os.path.normpath(remote_mnt)
    if not fp.startswith(remote_mnt):
        msg = "File {0} not located under remote mount point {1}"
        raise ValueError(msg.format(fp, remote_mnt))
    # Remove the remote mount point
    rel_fp = os.path.relpath(fp, remote_mnt)
    # Prepend the local mount point
    local_fp = os.path.join(local_mnt, rel_fp)
    return local_fp


class IlluminaFastqFileSet(object):
    allowed_file_extensions = [".fastq.gz", "fastq"]
    r1_code = "R1"
    r2_code = "R2"
    i1_code = "I1"
    i2_code = "I2"

    def __init__(self, r1_filepath):
        self.r1_filepath = r1_filepath

    @property
    def file_extension(self):
        for ext in self.allowed_file_extensions:
            if self.r1_filepath.endswith(ext):
                return ext
        raise ValueError("File extension for {0} not in {1}".format(
            self.r1_filepath, self.allowed_file_extensions))

    @property
    def is_gzip(self):
        return self.r1_filepath.endswith(".gz")

    @property
    def r1_base_filename(self):
        r1_filename = os.path.basename(self.r1_filepath)
        ext = self.file_extension
        nchar_ext = len(ext)
        return r1_filename[:-nchar_ext]
    
    @property
    def fastq_dir(self):
        return os.path.dirname(self.r1_filepath)
    
    def _illumina_fp(self, read_code):
        # From BaseSpace docs, format is SampleName_S1_L001_R1_001.fastq.gz
        # The docs indicate that final part is always '001'.
        # Nevertheless, allow other filenames if they contain the R1 code.
        # Find the rightmost instance of R1 and replace it.
        fp_left, r1, fp_right = self.r1_filepath.rpartition(self.r1_code)
        # Throw an error if the R1 code doesn't appear in the filepath
        if r1 != self.r1_code:
            raise ValueError("Could not find {0} in filepath {1}".format(
                self.r1_code, self.r1_filepath))
        return fp_left + read_code + fp_right

    @property
    def r2_filepath(self):
        return self._illumina_fp(self.r2_code)

    @property
    def i1_filepath(self):
        return self._illumina_fp(self.i1_code)

    @property
    def i2_filepath(self):
        return self._illumina_fp(self.i2_code)

    def open(self, fp):
        if self.is_gzip:
            return gzip.open(fp, mode="rt")
        else:
            return open(fp)

    def existing_file_set(self):
        fps = [
            self.r1_filepath, self.r2_filepath,
            self.i1_filepath, self.i2_filepath,
        ]
        return [self.open(fp) if os.path.exists(fp) else None for fp in fps]


# The plan:
#  1. Use JSON output from registry website
#     to build table of samples and grab file.
#     This gets rid of --sqlite-db and the registry
#     stuff in python.
#  2. Use only relative filepaths in the registry,
#     so we can get rid of the --local-mnt and --remote-mnt
#     arguments
#  3. Don't do the demultiplexing here; write a script to
#     run dnabc.py at the destination.
#  Now we are completely decoupled from the registry and dnabc.py
#  and this stuff gets moved into a new repo.
def export_samples(argv=None, db=REGISTRY_DATABASE):
    p = argparse.ArgumentParser()
    p.add_argument(
        "run_accession", type=int, help="Run accession number")
    p.add_argument("--output-dir", default="fastq_data",
        help="Output directory (default: %(default)s)")
    p.add_argument("--base-dir", default="/mnt/isilon/microbiome/",
        help="Base directory for relative filepaths in database")
    p.add_argument("--local-mnt", help="Local mount point")
    p.add_argument("--remote-mnt", help="Remote mount point")
    p.add_argument("--sqlite-db", help="Registry database file")
    args = p.parse_args(argv)

    if args.sqlite_db:
        db = RegistryDatabase(args.sqlite_db)

    run_fp = db.query_run_file(args.run_accession)
    if run_fp is None:
        raise ValueError("Run {0} not found.".format(args.run_accession))
    sample_barcodes = db.query_sample_barcodes(args.run_accession)

    demultiplex_from_registry(
        run_fp, sample_barcodes, args.output_dir, args.base_dir,
        args.local_mnt, args.remote_mnt)


def demultiplex_from_registry(
        r1_filepath, sample_barcodes, output_dir, base_dir,
        local_mnt, remote_mnt):
    # Do this first in case there is an error
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    fastq_dir = os.path.join(output_dir, "per_sample_fastq")
    if not os.path.exists(fastq_dir):
        os.mkdir(fastq_dir)

    # Get the absolute filepath to the R1 file
    r1_filepath = absolute_filepath(r1_filepath, base_dir)
    if local_mnt and remote_mnt:
        run_fp = remount_filepath(r1_filepath, remote_mnt, local_mnt)
    if not os.path.exists(r1_filepath):
        raise FileNotFoundError("Run file {0} not found".format(run_fp))
    # Get the file set from the R1 file
    fs = IlluminaFastqFileSet(r1_filepath)

    # From here down, we are heavily reliant on classes from dnabc
    # Consider wrapping this up in a function from dnabc
    samples = [Sample(name, bc) for name, bc in sample_barcodes]
    assigner = BarcodeAssigner(samples, revcomp=True)
    writer = PairedFastqWriter(fastq_dir)
    seq_file = SequenceFile(*fs.existing_file_set())
    seq_file.demultiplex(assigner, writer)
