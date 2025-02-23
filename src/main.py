# .venv/Scripts/activate
# python src/main.py

from __future__ import annotations

import shutil
import sys

from rekursion import get_filepaths_ancor
from utils.beautify import beautify_file
from utils.file import create_folder
from utils.globals import BASE_PATH
from utils.trace import Trace

DATA_PATH = BASE_PATH / "data"
IMPORT_PATH = DATA_PATH / "import"
EXPORT_PATH = DATA_PATH / "export"

EXCLUDE = {
    "folder": [".git", ".venv", "__pycache__", "__MACOSX"],
    "files": [],
}

def main() -> None:
    files, _dirs, _error = get_filepaths_ancor( IMPORT_PATH, exclude = EXCLUDE )
    for file in files:
        source = IMPORT_PATH / file
        dest   = EXPORT_PATH / file

        if source.suffix == ".js":
            beautify_file( "JS", source.parent, source.name, dest.parent, dest.name.replace(".min.", ".max.") )

        elif source.suffix == ".css":
            beautify_file( "CSS", source.parent, source.name, dest.parent, dest.name )

        elif source.suffix == ".json":
            beautify_file( "JSON", source.parent, source.name, dest.parent, dest.name )

        elif source.suffix in [".xml", ".rels"]:
            beautify_file( "XML", source.parent, source.name, dest.parent, dest.name )

        else:
            create_folder(dest.parent)
            shutil.copy2(source, dest)
            Trace.info( f"copy '{source}'" )


if __name__ == "__main__":
    Trace.set( debug_mode=True, timezone=False )
    Trace.action(f"Python version {sys.version}")

    try:
        main()
    except KeyboardInterrupt:
        Trace.exception("KeyboardInterrupt")
        sys.exit()
