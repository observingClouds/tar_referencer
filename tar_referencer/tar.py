"""Create tar archives"""
import argparse
import glob
import itertools
import os
import tarfile

import numpy as np


def pack_to_tar(directory, tar_fmt, max_size=np.inf, verbose=False):
    """Pack dataset into tar container"""
    files = itertools.chain(
        sorted(glob.iglob(directory + ".**", recursive=True)),
        sorted(glob.iglob(directory + "**", recursive=True)),
    )
    tar_file = 1
    last_file = None
    tar = tarfile.open(tar_fmt.format(tar_file), "w")

    while True:
        try:
            if last_file is None:
                file = next(files)
            else:
                if verbose:
                    print(f"Opening tar file {tar_fmt.format(tar_file)}")
                tar = tarfile.open(tar_fmt.format(tar_file), "w")
                file = last_file
        except StopIteration:
            tar.close()
            break
        file_size = os.path.getsize(file)
        if file_size > max_size:
            raise ValueError(
                f"Warning: File {file} is larger than given tar limitations"
            )
        elif file_size + tar.offset > max_size:
            last_file = file
            tar_file += 1
            tar.close()
            continue
        else:
            if verbose:
                print(f"Add {file} to archive")
            tar.add(file, recursive=False)
            last_file = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Directory (e.g. zarr base directory) that should be packed into a tar file",
    )
    parser.add_argument(
        "-t",
        "--tar",
        help="Filename format of the resulting tar files e.g. output{:03d}.tar",
    )
    parser.add_argument(
        "-s",
        "--maxsize",
        type=int,
        help="Maximum filesize of a tar file, before a new one is created",
    )
    args = parser.parse_args()
    pack_to_tar(args.input, args.tar, args.maxsize)


if __name__ == "__main__":
    main()
