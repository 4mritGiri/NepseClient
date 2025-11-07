# Configuration file for the Sphinx documentation builder.
"""Sphinx configuration for NEPSE Client documentation."""
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "NEPSE Client"
copyright = "2025, Amrit Giri"
author = "Amrit Giri"
# You can dynamically get the version from your package if needed,
# e.g., import nepse_client; version = nepse_client.__version__
# For now, using a placeholder or the version from your setup.py
version = "1.0.0"  # Replace with your actual version
release = version  # Often the same as version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Core autodoc functionality
    "sphinx.ext.viewcode",  # Add source code links
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.intersphinx",  # Link to other documentation (e.g., Python stdlib)
    # 'myst_parser',          # If you need to include Markdown files
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # Or another theme like 'alabaster', 'basic', etc.
html_static_path = ["_static"]

# -- Autodoc Configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when available
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Default options for autodoc directives
autodoc_default_options = {
    "members": True,  # Document members
    "undoc-members": True,  # Include members without docstrings
    "show-inheritance": True,  # Show inheritance chain
    # 'special-members': '__init__', # Document __init__ methods
}

# -- Intersphinx Configuration -----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    # Add mappings for other libraries you use, e.g., httpx
    "httpx": ("https://www.python-httpx.org/", None),
    # 'numpy': ('https://numpy.org/doc/stable/', None),
    # 'pandas': ('https://pandas.pydata.org/docs/', None),
    # 'django': ('https://docs.djangoproject.com/en/stable/', None),
    # 'click': ('https://click.palletsprojects.com/en/8.1.x/', None),
    # 'click': ('https://click.palletsprojects.com/en/stable/', None),
}

# -- Napoleon Configuration --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

# napoleon_google_docstring = True  # Handled by the default True value
# napoleon_numpy_docstring = True   # Handled by the default True value
napoleon_include_init_with_doc = False  # Exclude __init__ docstrings by default
napoleon_include_private_with_doc = False  # Exclude private members by default
napoleon_attr_annotations = True  # Enable parsing of attribute annotations
