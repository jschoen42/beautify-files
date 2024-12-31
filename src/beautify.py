"""
    © Jürgen Schoenemeyer, 31.12.2024

    PUBLIC:
     - beautify_file( file_type: str, source_path: Path | str, source_filename: str, dest_path: Path | str, dest_filename: str ) -> bool:
        - file_type = "JS" | "CSS" | "JSON" | "XML"

    PRIVAT:
     - expand_js(text: str) -> str:
     - expand_css(text: str) -> str:

"""

import os
import json

from pathlib import Path

import jsbeautifier
import cssbeautifier
from lxml import etree

from utils.trace     import Trace
from utils.decorator import duration
from utils.util      import import_text, export_text

expand_data_js: dict = {
    "!0":  "true",
    "!1":  "false",

    "1e3": "1000",
    "1e4": "10000",
    "6e4": "60000",
    "1e5": "100000",
    "1e6": "1000000",
    "1e7": "10000000",

    "36e5": "3600000",
    "36e9": "36000000000",

    "~~(": "Math.floor(",
}

expand_data_css: dict = {
    ">":      " > ",
    "  >  ":  " > ",

    "\n  }": ";\n  }",
    "\n}":   ";\n}",
    ";  ;":  ";",
    ";;":    ";",

    "};":    "}",
}

def expand_js(text: str) -> str:
    for key, value in expand_data_js.items():
        text = text.replace(key, value)
    return text

def expand_css(text: str) -> str:
    for key, value in expand_data_css.items():
        text = text.replace(key, value)
    return text

@duration("beautify '{1}\{2}'")
def beautify_file( file_type: str, source_path: Path | str, source_filename: str, dest_path: Path | str, dest_filename: str ) -> bool:
    source = Path(source_path, source_filename)
    dest   = Path(dest_path, dest_filename)

    text = import_text(source.parent, source.name)
    if text is None:
        return False

    mtime = os.stat(source).st_mtime

    opts = jsbeautifier.default_options()
    opts.indent_size = 2

    if file_type == "JS":
        data = expand_js( jsbeautifier.beautify(text, opts) )

    elif file_type == "CSS":
        data = expand_css( cssbeautifier.beautify(text, opts) )

    elif file_type == "JSON":
        data = json.dumps(json.loads(text), indent=2)

    elif file_type == "XML":
        x = etree.fromstring(text)
        data = etree.tostring(x, pretty_print=True, encoding=str)

    else:
        Trace.error( f"unknown file type '{file_type}'" )
        return False

    return export_text(dest.parent, dest.name, data, timestamp = mtime)
