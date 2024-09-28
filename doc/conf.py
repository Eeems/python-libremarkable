import datetime
import os
import sys

from intersphinx_registry import get_intersphinx_mapping

sys.path.insert(0, os.path.abspath(".."))

year = datetime.datetime.today().year

project = "Python libremarkable"
copyright = f"2024-{year}, Eeems"
author = "Nathaniel 'Eeems' van Diepen"

html_title = "Python libremarkable"
master_doc = "sitemap"
html_permalinks_icon = "#"

autodoc_default_options = {
    "members": "",
    "special-members": None,
    "member-order": "groupwise",
}
autodoc_typehints_description_target = "all"
autodoc_type_aliases = {
    "Keymap": "libremarkable.Keymap",
    "Framebuffer": "libremarkable._framebuffer.Framebuffer",
    "iter": "typing.Iterable",
}

extensions = [
    "sphinxcontrib.fulltoc",
    "sphinx.ext.autodoc",
    "sphinx_toolbox.more_autodoc.overloads",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

intersphinx_mapping = get_intersphinx_mapping(packages={"python", "pillow"})
intersphinx_mapping.update(
    {"evdev": ("https://python-evdev.readthedocs.io/en/latest/", None)}
)
