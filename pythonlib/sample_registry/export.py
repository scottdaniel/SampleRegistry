import argparse
import os
import shlex

import requests


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

    def existing_filepaths(self):
        fps = [
            self.r1_filepath, self.r2_filepath,
            self.i1_filepath, self.i2_filepath,
        ]
        return [fp if os.path.exists(fp) else None for fp in fps]


CHOP_DATA_DIR = "/mnt/isilon/microbiome/"
CHOP_REGISTRY_URL = "http://reslnmbiomea01.research.chop.edu/registry/"
def export_samples(argv=None, run_info=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "run_accession", type=int, help="Run accession number")
    p.add_argument("--output-dir", default="fastq_data",
        help="Output directory (default: %(default)s)")
    p.add_argument("--base-dir", default=CHOP_DATA_DIR,
        help="Base directory for data files")
    p.add_argument("--registry-url", default=CHOP_REGISTRY_URL,
        help="Registry URL")
    args = p.parse_args(argv)

    if run_info is None:
        run_json_url = "{0}runs/{1}.json".format(
            args.registry_url, args.run_accession)
        r = requests.get(run_json_url)
        run_info = r.json()

    run_fp = run_info["run"]["data_uri"]
    samples = run_info["samples"]
    sample_barcodes = [
        (s["sample_name"], s["barcode_sequence"]) for s in samples]

    # Fix absolute filepaths in the database
    relative_run_fp = remove_prefix(run_fp, CHOP_DATA_DIR)
    absolute_run_fp = os.path.join(args.base_dir, relative_run_fp)

    # Error out now if we can't find the run file
    if not os.path.exists(absolute_run_fp):
        msg = "Run file {0} not found".format(absolute_run_fp)
        raise FileNotFoundError(msg)

    # Next, error out if we can't create the output directory
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    # Get the file set from the R1 file
    fs = IlluminaFastqFileSet(absolute_run_fp)
    r1_fp, r2_fp, i1_fp, i2_fp = fs.existing_filepaths()

    barcode_fp = os.path.join(args.output_dir, "barcodes.txt")
    with open(barcode_fp, "w") as f:
        for name, bc in sample_barcodes:
            f.write("{0}\t{1}\n".format(name, bc))

    dnabc_script_fp = os.path.join(args.output_dir, "run_dnabc.sh")
    fastq_dir = os.path.join(args.output_dir, "per_sample_fastq")
    with open(dnabc_script_fp, "w") as f:
        f.write("#!/bin/bash\n")
        cmd = dnabc_command(
            r1_fp, r2_fp, i1_fp, i2_fp, barcode_fp, fastq_dir, revcomp=True)
        f.write(cmd)
        f.write("\n")
    make_executable(dnabc_script_fp)


# From https://stackoverflow.com/a/16891427
def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s


# From https://stackoverflow.com/a/30463972
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


def dnabc_command(
        r1_fp, r2_fp, i1_fp, i2_fp, barcode_fp, fastq_dir, revcomp=True):
    cmd_parts = [
        "dnabc.py",
        "--barcode-file", shlex.quote(barcode_fp),
        "--forward-reads", shlex.quote(r1_fp),
        "--reverse-reads", shlex.quote(r2_fp),
    ]
    if i1_fp is not None:
        cmd_parts.extend(["--index-reads", shlex.quote("i1_fp")])
        if i2_fp is not None:
            cmd_parts.extend(["--reverse-index-reads", shlex.quote("i2_fp")])
    cmd_parts.extend(["--output-dir", shlex.quote(fastq_dir)])
    if revcomp:
        cmd_parts.append("--revcomp")
    return " ".join(cmd_parts)
