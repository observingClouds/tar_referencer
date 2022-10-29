"""Test collection for testing generation of parquet
reference filesystems based on tar files
"""
import glob
import itertools
import shutil
import tarfile

import pytest
import xarray as xr
from xarray.testing import assert_equal

import tar_referencer.referencer as r


@pytest.fixture(scope="session")
def tmp_test_folder(tmpdir_factory):
    fn = tmpdir_factory.mktemp("test")
    return fn
    shutil.rmtree(str(fn))


def create_test_tar(tmp_test_folder):
    print("helllo")
    xr.tutorial.load_dataset("air_temperature").chunk(
        {"time": 100, "lat": 5, "lon": 5}
    ).to_zarr(str(tmp_test_folder) + "/example.zarr")
    with tarfile.open(f"{tmp_test_folder}/example.zarr.tar", "w") as tar:
        zarr_base = f"{tmp_test_folder}/example.zarr/"
        zarr_files = itertools.chain(
            glob.iglob(zarr_base + "**", recursive=True),
            glob.iglob(zarr_base + ".**", recursive=True),
        )
        for name in zarr_files:
            arcname = name.replace(str(tmp_test_folder) + "/example.zarr/", "")
            if arcname == "":
                print(name)
                continue
            tar.add(name, recursive=False, arcname=arcname)


def test_preffs_creation(
    tmp_test_folder, tar_fn="example.zarr.tar", output_folder=tmp_test_folder
):
    create_test_tar(tmp_test_folder)
    parquet_filename = f"{tmp_test_folder}/example.zarr.tar.preffs"
    tar_fn = f"{tmp_test_folder}/{tar_fn}"
    r.create_preffs(tar_fn, parquet_filename)


def test_valid_preffs(
    tmp_test_folder, preffs_fn="example.zarr.tar.preffs", original_fn="example.zarr"
):
    storage_options = {"preffs": {"prefix": str(tmp_test_folder) + "/"}}
    print(storage_options)
    ds_preffs = xr.open_zarr(
        f"preffs::{tmp_test_folder}/{preffs_fn}", storage_options=storage_options
    )
    ds = xr.open_zarr(f"{tmp_test_folder}/{original_fn}")
    assert_equal(ds_preffs, ds)
