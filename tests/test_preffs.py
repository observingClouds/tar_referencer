"""Test collection for testing generation of parquet
reference filesystems based on tar files
"""
import glob
import os
import shutil

import pandas as pd
import pytest
import xarray as xr
from xarray.testing import assert_equal

import tar_referencer.referencer as r
import tar_referencer.tar as t


@pytest.fixture(scope="session")
def tmp_test_folder(tmpdir_factory):
    fn = tmpdir_factory.mktemp("test")
    return fn
    shutil.rmtree(str(fn))


def create_test_tar(tmp_test_folder):
    xr.tutorial.load_dataset("air_temperature").chunk(
        {"time": 100, "lat": 5, "lon": 5}
    ).to_zarr(str(tmp_test_folder) + "/example.zarr")
    os.chdir(os.path.join(tmp_test_folder, "example.zarr"))
    t.pack_to_tar("", os.path.join(tmp_test_folder, "example.zarr.{:03d}.tar"), 1000000)


def test_preffs_creation(
    tmp_test_folder, tar_fn="example.zarr.*.tar", output_folder=tmp_test_folder
):
    create_test_tar(tmp_test_folder)
    parquet_filename = f"{tmp_test_folder}/example.zarr.tar.preffs"
    tar_fn = f"{tar_fn}"
    os.chdir(tmp_test_folder)
    r.create_preffs(sorted(glob.glob(tar_fn)), parquet_filename)


def test_valid_preffs(
    tmp_test_folder, preffs_fn="example.zarr.tar.preffs", original_fn="example.zarr"
):
    storage_options = {"preffs": {"prefix": str(tmp_test_folder) + "/"}}
    ds_preffs = xr.open_zarr(
        f"preffs::{tmp_test_folder}/{preffs_fn}", storage_options=storage_options
    )
    ds = xr.open_zarr(f"{tmp_test_folder}/{original_fn}")
    assert_equal(ds_preffs, ds)


def test_sorted_preffs(tmp_test_folder, preffs_fn="example.zarr.tar.preffs"):
    df = pd.read_parquet(os.path.join(tmp_test_folder, preffs_fn))
    assert (
        len(df.path.unique()) > 1
    ), "this test cannot be done if only one tar archive is referenced"
    assert df.path.is_monotonic_increasing, "preffs paths are not sorted by filename"
