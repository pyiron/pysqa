# Contributing to pysqa

Contributions to `pysqa` are very welcome — whether you want to report a bug,
request a feature, improve the documentation, or submit code. This document
explains how to get involved.

By participating in this project you agree to abide by the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting issues

If you find a bug or unexpected behaviour, please open an issue on the
[GitHub issue tracker](https://github.com/pyiron/pysqa/issues). A good bug
report includes:

* the version of `pysqa` you are using (`python -c "import pysqa; print(pysqa.__version__)"`),
* your operating system and Python version,
* the queuing system you are talking to (SLURM, Flux, SGE, ...),
* a minimal example that reproduces the problem, and
* the full error message and traceback.

Before opening a new issue, please search the existing issues to avoid
duplicates.

## Requesting features

Feature requests are tracked as issues as well. Please describe the use case you
have in mind and, if possible, how you imagine the feature working from a user's
point of view.

## Seeking support

If you have a usage question rather than a bug report, please consult the
[documentation](https://pysqa.readthedocs.io) first. The
[example notebooks](notebooks) and the
[debugging guide](https://pysqa.readthedocs.io/en/latest/debug.html) cover the
most common configurations. If your question is not answered there, feel free to
open an issue with the `question` label.

## Contributing code

`pysqa` is a spin-off of the [pyiron project](https://pyiron.org) and follows a
standard fork-and-pull-request workflow.

### 1. Set up a development environment

`pysqa` is developed against a [conda](https://docs.conda.io) environment. The
pinned dependencies used in continuous integration are defined in
[`.ci_support/environment.yml`](.ci_support/environment.yml):

```bash
git clone https://github.com/pyiron/pysqa.git
cd pysqa
conda env create -f .ci_support/environment.yml -n pysqa
conda activate pysqa
pip install -e . --no-deps --no-build-isolation
```

### 2. Make your changes

* Create a feature branch for your work (`git checkout -b my-feature`).
* Add or update tests in the [`tests`](tests) directory for any behaviour you
  change.
* Keep the public API documented with type hints and docstrings.

### 3. Check code style and types

Code style is enforced automatically. The quickest way to stay consistent is to
install the [pre-commit](https://pre-commit.com) hooks, which run
[ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
pip install pre-commit
pre-commit install
```

You can run the same checks manually:

```bash
ruff check src/pysqa        # linting
ruff format src/pysqa       # formatting
mypy --ignore-missing-imports src/pysqa   # static type checking
```

### 4. Run the tests

```bash
python -m unittest discover tests        # or: pytest tests/unit
```

Some tests require optional dependencies (`paramiko`, `tqdm`, `flux`) and are
skipped automatically when these are not installed. The full test matrix —
including SLURM and Flux integration tests across several operating systems and
Python versions — runs automatically on every pull request.

### 5. Open a pull request

Push your branch to your fork and open a pull request against the `main` branch.
Please describe what your change does and reference any related issues.
Continuous integration has to pass before a pull request can be merged.

Thank you for helping to improve `pysqa`!
