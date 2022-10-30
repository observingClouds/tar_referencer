import argparse
import os
import tarfile as tf

import pandas as pd


class archive_reference:
    def __init__(self):
        self.tar_files = []
        self.index_files = {}

    def add_tar(self, tar_file):
        if isinstance(tar_file, str):
            self.tar_files.append(tar_file)
        elif isinstance(tar_file, list):
            self.tar_files.extend(tar_file)
        else:
            raise TypeError("tar file(s) must be a string or list")

    def _index_tar(self, tar_file):
        with tf.open(tar_file, "r|") as db:
            index = {}
            for tarinfo in db:
                index[tarinfo.name] = {
                    "key": tarinfo.name,
                    "offset": tarinfo.offset_data,
                    "size": tarinfo.size,
                }
        index_df = pd.DataFrame.from_dict(index, orient="index")
        index_df["path"] = os.path.basename(tar_file)
        index_df["raw"] = None
        return index_df

    @property
    def index(self):
        if hasattr(self, "_index"):
            return self._index
        else:
            return self._get_index()

    def _get_index(self):
        indices = []
        for tar_file in self.tar_files:
            indices.append(self._index_tar(tar_file))
        index_df = pd.concat(indices)
        self._index = index_df.sort_values("key")
        self._index = self._index.reindex(
            columns=["key", "path", "offset", "size", "raw"]
        )
        self._index = self._index.set_index("key")
        return self._index

    def to_parquet(self, filename):
        """export references to parquet file to be used with preffs"""
        self.index.to_parquet(filename)


def create_preffs(tar_files, reference_file):
    """create parquet reference file
    tar_files : tar files to be referenced
    reference_file : filename of resulting reference file
    """
    ar = archive_reference()
    ar.add_tar(tar_files)
    ar.to_parquet(reference_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tarfiles", nargs="+", help="Tar-files to index")
    parser.add_argument(
        "-p", "--parquet", help="Filename of resulting parquet reference file"
    )
    args = parser.parse_args()
    create_preffs(args.tarfiles, args.parquet)


if __name__ == "__main__":
    main()
