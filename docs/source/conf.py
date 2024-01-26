# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pysqa'
copyright = '2023, Jan Janssen'
author = 'Jan Janssen'
release = '0.0.22'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser"]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_logo = "../_static/pyiron-logo.png"
    html_favicon = "../_static/pyiron_logo.ico"
except ImportError:
    html_theme = 'alabaster'

html_static_path = ['_static']
