from pathlib import Path
from jinja2 import Environment
from followthemoney import model

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "followthemoney"
copyright = "2021, OCCRP"
author = "OCCRP"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

print("Generating FtM schema documentation...")

sphinx_path = Path(__file__).parent
env = Environment()
with open(sphinx_path.joinpath("_templates/schema.jinja2"), "r") as fh:
    template = env.from_string(fh.read())
# schema_path = sphinx_path.joinpath("schema")
# schema_path.mkdir(exist_ok=True)
# for name, schema in model.schemata.items():
#     file_name = schema_path.joinpath(f"{name.lower()}.rst")
#     with open(file_name, "w") as fh:
#         fh.write(template.render(schema=schema, model=model))

file_name = sphinx_path.joinpath("model.rst")
with open(file_name, "w") as fh:
    fh.write(template.render(model=model))
