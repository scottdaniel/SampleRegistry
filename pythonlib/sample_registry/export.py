import argparse
import gzip
import os


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

    def existing_file_set(self):
        fps = [
            self.r1_filepath, self.r2_filepath,
            self.i1_filepath, self.i2_filepath,
        ]
        return [fp if os.path.exists(fp) else None for fp in fps]


def export_samples(argv=None, db=REGISTRY_DATABASE):
    p = argparse.ArgumentParser()
    p.add_argument(
        "run_accession", type=int, help="Run accession number")
    p.add_argument("-base-dir", default="/mnt/isilon/microbiome/",
        help="Base directory for relative filepaths in database")
    p.add_argument("--local-mnt", help="Local mount point")
    p.add_argument("--remote-mnt", help="Remote mount point")
    args = p.parse_args(argv)
    
    # Use current dir for output
    output_dir = os.getcwd()

    run_info = db._query_run(args.run_accession)
    if run_info is None:
        raise ValueError("Run {0} not found.".format(args.run_accession))
    run_fp = run_info[4]

    # Get the absolute filepath to the R1 file
    run_fp = absolute_filepath(run_fp, args.base_dir)
    if args.local_mnt and args.remote_mnt:
        run_fp = remount_filepath(run_fp, args.remote_mnt, args.local_mnt)
    if not os.path.exists(run_fp):
        raise FileNotFoundError("Run file {0} not found".format(run_fp))
        
    # Get the sample names and barcodes
    sample_barcodes = db.query_sample_barcodes(args.run_accession)
    samples = [Sample(name, bc) for name, bc in sample_barcodes]

    # Make a new assigner with the sample list
    assigner = BarcodeAssigner(samples, revcomp=True)

    # Make a FastqSequenceFile object
    fs = IlluminaFastqFileSet(run_fp)
    seq_file = SequenceFile(**fs.existing_file_set())

    # Make a writer
    writer = PairedFastqWriter(output_dir)
    seq_file.demultiplex(assigner, writer)
