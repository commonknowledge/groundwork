#!/usr/bin/env python
import os
import re
import sys
from pathlib import Path

import django
import pdoc
from django.conf import settings
from django.template import Context, Template
from pdoc.html_helpers import to_markdown

# Setup directory locations
OUTPUT_DIR = Path.cwd() / "docs" / "api"
TEMPLATE_PATH = Path.cwd() / "docs" / "templates"

sys.path.append(os.path.abspath("./"))

# Override the default pdoc markdown template cos it's ugly
pdoc.tpl_lookup.directories.insert(
    0,
    str(TEMPLATE_PATH),
)

# Specify settings module and setup django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()


modules = [app for app in settings.INSTALLED_APPS if app.startswith("pyck.")]
context = pdoc.Context()

modules = [pdoc.Module(mod, context=context) for mod in modules]
pdoc.link_inheritance(context)


def recursive_htmls(mod):
    yield mod.name, mod.text()
    for submod in mod.submodules():
        yield from recursive_htmls(submod)


if __name__ == "__main__":
    for mod in modules:
        for module_name, html in recursive_htmls(mod):
            docs_path = OUTPUT_DIR / f"{module_name}.md"

            with open(str(docs_path), "w", encoding="utf8") as f:
                f.write(html)
