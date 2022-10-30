# Converting tar archives into a reference filesystem

Zarr files can challenge metadata-server of HPC systems due to their millions of files.
One way to circumvent this challenge is to collect all files in a file container, e.g. in tar files
and create a look-up table of byte ranges where the content of each file is saved within
the container. Tar-ing zarr files makes it also easy to store and reuse data on tape-archives.

*tar_referencer* creates these look-up tables that can be used with the [preffs package](https://github.com/d70-t/preffs).

## Usage

The package can be installed with
```
pip install git+https://github.com/observingClouds/tar_referencer.git
```

The look-up files (parquet reference files) are created with

```python
tar_referencer -t file.*.tar -p file_index.preffs
```

If zarr files have been packed into tars and indexed with *tar_referencer* the tars can be opened with:
```python
import xarray as xr
storage_options={"preffs":{"prefix":/path/to/tar/files/"}}
ds = xr.open_zarr("preffs::file_index.preffs", storage_options=storage_options)
```

### Creating tar files
Technically all sorts of tar files can be referenced. However, *tar_referencer* currently does only supports tar files that are split at the file level. Tar files that are split within the header or data block are not supported.
> **Warning**
> This does not work:
> ```
> tar -cvf - big.tar | split --bytes=32000m --suffix-length=3 --numeric-suffix - part%03d.tar
> ```

To generate compatible tar files from zarr files or other directory structures, *tar_referencer* provides `tar_creator`:
```
tar_creator -i dataset.zarr -t dataset_part{:03d}.tar -s MAX_SIZE_BYTES
```
where `MAX_SIZE_BYTES` is the maximum size of a tar file, before writing further output to an additional archive.

To split already existing tar files, [Splitar](https://github.com/monoid/splitar) has been successfully tested.
```
splitar -S 32000m big.tar part.tar-
```

## Tips and tricks

For very big zarr-datasets, especially those that contain several variables, it might be advisable to pack each variable-subfolder
of the zarr file into their own set of tars. The benefit of this approach is that only those tars need to be downloaded/retrieved that
are actually containing the variable of interest. For each of these sets a separate look-up table can be generated and merged to an overaching look-up
table containing the entire dataset

```python
import pandas as pd
df_coords = pd.read_parquet("file_index.coords.preffs")
df_var1 = pd.read_parquet("file_index.var1.preffs")
df_var2 = pd.read_parquet("file_index.var2.preffs")
df_entire_dataset = pd.concat([df_coords, df_var1, df_var2]).sort_index()
df_entire_dataset.to_parquet("entire_dataset.preffs")
```
