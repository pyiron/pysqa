# Installation
The `pysqa` package can be installed either via `pip` or `conda`. While most HPC systems use Linux these days, the `pysqa` package can be installed on all major operation systems. In particular for connections to remote HPC clusters it is required to install `pysqa` on both the local system as well as the remote HPC cluster. In this case it is highly recommended to use the same version of `pysqa` on both systems. 

## pypi-based installation
`pysqa` can be installed from the python package index (pypi) using the following command: 
```
pip install pysqa
```
On `pypi` the `pysqa` package exists in three different versions: 

* `pip install pysaq` - base version - with minimal requirements only depends on `jinja2`, `pandas` and `pyyaml`.
* `pip install pysaq[sge]` - sun grid engine (SGE) version - in addition to the base dependencies this installs `defusedxml` which is required to parse the `xml` files from `qstat`. 
* `pip install pysaq[remote]` - remote version - in addition to the base dependencies this installs `paramiko` and `tqdm`, to connect to remote HPC clusters using SSH and report the progress of the data transfer visually. 

## conda-based installation 
The `conda` package combines all dependencies in one package: 
```
conda install -c conda-forge pysqa
```
When resolving the dependencies with `conda` gets slow it is recommended to use `mamba` instead of `conda`. So you can also install `pysqa` using: 
```
mamba install -c conda-forge pysqa
```

