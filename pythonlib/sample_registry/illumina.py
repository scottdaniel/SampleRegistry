import os.path
import re


def parse_illumina_fastq_header(f):
    line = next(f).strip()
    if not line.startswith("@"):
        raise ValueError("Not a FASTQ header line")
    # Remove first character, @
    line = line[1:]
    word1, _, word2 = line.partition(" ")

    keys1 = ("instrument", "run_number", "flowcell_id", "lane")
    vals1 = dict((k, v) for k, v in zip(keys1, word1.split(":")))

    keys2 = ("read", "is_filtered", "control_number", "index_reads")
    vals2 = dict((k, v) for k, v in zip(keys2, word2.split(":")))

    vals1.update(vals2)
    return vals1


# From https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch04s16.html
def splitall(path):
    allparts = []
    while 1:
        left, right = os.path.split(path)
        if left == path:  # sentinel for absolute paths
            allparts.insert(0, left)
            break
        elif right == path: # sentinel for relative paths
            allparts.insert(0, right)
            break
        else:
            path = left
            allparts.insert(0, right)
    return allparts


def parse_illumina_folder_date(dirname):
    dirs = splitall(dirname)
    rundir = dirs[1]
    if re.match("\\d{6}_", rundir):
        year = rundir[0:2]
        month = rundir[2:4]
        day = rundir[4:6]
        return "20{0}-{1}-{2}".format(year, month, day)
    return None
