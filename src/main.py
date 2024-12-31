# .venv/Scripts/activate
# python src/main.py

import sys
import shutil

from utils.globals import BASE_PATH
from utils.trace   import Trace
from utils.file    import create_folder

from rekursion import get_filepaths_ancor
from beautify  import beautify_file

DATA_PATH = BASE_PATH / "data"
IMPORT_PATH = DATA_PATH / "import"
EXPORT_PATH = DATA_PATH / "export"

def main():
    files, _dirs, _error = get_filepaths_ancor( IMPORT_PATH )
    for file in files:
        source = IMPORT_PATH / file
        dest   = EXPORT_PATH / file

        if source.suffix == ".js":
            beautify_file( "JS", source.parent, source.name, dest.parent, dest.name )
            continue

        if source.suffix == ".css":
            beautify_file( "CSS", source.parent, source.name, dest.parent, dest.name )
            continue

        if source.suffix == ".json":
            beautify_file( "JSON", source.parent, source.name, dest.parent, dest.name )
            continue

        if source.suffix == ".xml":
            beautify_file( "XML", source.parent, source.name, dest.parent, dest.name )
            continue

        if source.suffix == ".png":
            # print( "JSON" )
            continue

        create_folder(dest.parent)
        shutil.copy2(source, dest)
        Trace.info( f"copy '{source}' -> '{dest}'" )

        # Trace.info( f"File '{source}' not supported" )


if __name__ == "__main__":
    Trace.set( debug_mode=True, timezone=False )
    Trace.action(f"Python version {sys.version}")

    try:
        main()
    except KeyboardInterrupt:
        Trace.exception("KeyboardInterrupt")
        sys.exit(0)
