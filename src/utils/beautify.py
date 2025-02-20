"""
    © Jürgen Schoenemeyer, 07.02.2025

    src/utils/beautify.py

    PUBLIC:
     - beautify_file( file_type: str, source_path: Path | str, source_filename: str, dest_path: Path | str, dest_filename: str ) -> bool:
        - file_type = "JS" | "CSS" | "JSON" | "XML"

    PRIVAT:
     - expand_js(text: str) -> str:
     - expand_css(text: str) -> str:
"""

import os
import json

from typing import Dict
from pathlib import Path

import jsbeautifier        # type: ignore[import-untyped]
import cssbeautifier       # type: ignore[import-untyped]
from lxml import etree

from utils.trace     import Trace
from utils.decorator import duration
from utils.file      import import_text, export_text

# print(etree)

expand_data_js: Dict[str, str] = {
    "!0":  "true",
    "!1":  "false",

    " 1e3":  " 1000",
    " 1e4":  " 10000",
    " 1e5":  " 100000",
    " 1e6":  " 1000000",
    " 1e7":  " 10000000",
    " 1e8":  " 100000000",
    " 1e9":  " 1000000000",
    " 1e10": " 10000000000",
    " 1e11": " 100000000000",
    " 1e12": " 1000000000000",
    " 1e13": " 10000000000000",
    " 1e14": " 100000000000000",
    " 1e15": " 1000000000000000",
    " 1e16": " 10000000000000000",

    "(1e3":  "(1000",
    "(1e4":  "(10000",
    "(1e5":  "(100000",
    "(1e6":  "(1000000",
    "(1e7":  "(10000000",
    "(1e8":  "(100000000",
    "(1e9":  "(1000000000",
    "(1e10": "(10000000000",
    "(1e11": "(100000000000",
    "(1e12": "(1000000000000",
    "(1e13": "(10000000000000",
    "(1e14": "(100000000000000",
    "(1e15": "(1000000000000000",
    "(1e16": "(10000000000000000",

    "[1e3":  "[1000",
    "[1e4":  "[10000",
    "[1e5":  "[100000",
    "[1e6":  "[1000000",
    "[1e7":  "[10000000",
    "[1e8":  "[100000000",
    "[1e9":  "[1000000000",
    "[1e10": "[10000000000",
    "[1e11": "[100000000000",
    "[1e12": "[1000000000000",
    "[1e13": "[10000000000000",
    "[1e14": "[100000000000000",
    "[1e15": "[1000000000000000",
    "[1e16": "[10000000000000000",

    "/1e3":  "/1000",
    "/1e4":  "/10000",
    "/1e5":  "/100000",
    "/1e6":  "/1000000",
    "/1e7":  "/10000000",
    "/1e8":  "/100000000",
    "/1e9":  "/1000000000",
    "/1e10": "/10000000000",
    "/1e11": "/100000000000",
    "/1e12": "/1000000000000",
    "/1e13": "/10000000000000",
    "/1e14": "/100000000000000",
    "/1e15": "/1000000000000000",
    "/1e16": "/10000000000000000",

    " -1e3":  " -1000",
    " -1e4":  " -10000",
    " -1e5":  " -100000",
    " -1e6":  " -1000000",
    " -1e7":  " -10000000",
    " -1e8":  " -100000000",
    " -1e9":  " -1000000000",
    " -1e10": " -10000000000",
    " -1e11": " -100000000000",
    " -1e12": " -1000000000000",
    " -1e13": " -10000000000000",
    " -1e14": " -100000000000000",
    " -1e15": " -1000000000000000",
    " -1e16": " -10000000000000000",

    " -2e3":  " -2000",
    " -4e3":  " -4000",
    " -8e3":  " -8000",

    " 4e3": " 4000",
    " 8e3": " 8000",

    " 31e3":  " 31000",
    " 6e4":   " 60000",
    " 36e4":  " 360000",
    " 36e5":  " 3600000",
    " 108e5": " 108000000",
    " 36e9":  " 36000000000",

    "(31e3":  "(31000",
    "(6e4":   "(60000",
    "(36e4":  "(360000",
    "(36e5":  "(3600000",
    "(108e5": "(108000000",
    "(36e9":  "(36000000000",

    "/31e3":  "/31000",
    "/6e4":   "/60000",
    "/36e4":  "/360000",
    "/36e5":  "/3600000",
    "/108e5": "/108000000",
    "/36e9":  "/36000000000",

    "~~(": "Math.floor(",
}

expand_data_css: Dict[str, str] = {
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

@duration("beautify '{1}\\{2}'")
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
        try:
            data = json.dumps(json.loads(text), indent=2)
        except ValueError as err:
            Trace.error( f"JSON parse error: {err} - {source}" )
            data = text

    elif file_type == "XML":
        try:
            x = etree.fromstring(text)
            data = etree.tostring(x, pretty_print=True, encoding=str)
        except ValueError as err:
            Trace.error( f"XML parse error: {err} - {source}" )
            data = text

    else:
        Trace.error( f"unknown file type '{file_type}'" )
        return False

    if export_text(dest.parent, dest.name, data, timestamp = mtime):
        return True
    else:
        return False
