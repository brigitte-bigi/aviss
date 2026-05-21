# makedoc.py
# Summary: Create the documentation of AViSS, using Clamming library.
# Usage: python makedoc.py
#
# This file is part of AViSS tool.
# (C) 2026 Brigitte Bigi, Laboratoire Parole et Langage,
# Aix-en-Provence, France.
#
# Use of this software is governed by the GNU Affero Public License, version 3.
#
# ---------------------------------------------------------------------------

import sys
import logging

import aviss
import aviss.core
try:
    from clamming import ClamsModules
    from clamming import ExportOptions
except ImportError:
    print("This program requires `Clamming` documentation generator.")
    print("It can be installed with: pip install ClammingPy.")
    print("See <https://pypi.org/project/Clamming/> for details.")
    sys.exit(-1)

# ---------------------------------------------------------------------------
logging.getLogger().setLevel(0)

# -------------------------------------------------
# List of modules to be documented: automatically create the documentation of
# all known classes of the following 'aviss' packages.
# -------------------------------------------------
packages = list()
packages.append(aviss.core)
packages.append(aviss)

# ----------------------------
# Options for exportation
# ----------------------------
opts_export = ExportOptions()
opts_export.software = 'AViSS ' + aviss.__version__
opts_export.copyright = aviss.__copyright__
opts_export.url = 'https://github.com/brigitte-bigi/AViSS.git'
opts_export.title = 'AViSS doc'
# ... statics is the relative path to a folder with the CSS, JS, etc.
opts_export.wexa_statics = './Whakerexa-2.1/wexa_statics'
opts_export.statics = './statics'
# ... the theme must correspond to a statics/<theme>.css file
opts_export.theme = 'light'
# ... the favicon and icon are files in the statics folder
opts_export.favicon = 'aviss.png'
opts_export.icon = 'aviss.png'
opts_export.readme = True

# -------------------------------------------------
# Generate documentation
# -------------------------------------------------
clams_modules = ClamsModules(packages)

# Export documentation into HTML files.
# One .html file = one documented class.
clams_modules.html_export_packages("docs", opts_export, "README.md")

# Export documentation into a Markdown file.
# One .md file = one documented module.
clams_modules.markdown_export_packages("docs", opts_export)
