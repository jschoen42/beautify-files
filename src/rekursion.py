"""
    © Jürgen Schoenemeyer, 03.02.2025

    PUBLIC:
     - get_filepaths_all( path: Path, exclude: dict = None ) -> Tuple[list, list, list]
     - get_filepaths_ancor( ancor_path: Path, exclude: dict = None ) -> Tuple[list, list, list]:
        - ancor path: relative/absolute path
        - folder, files, error paths: relative to ancor_path

"""

from typing import Tuple
from pathlib import Path

from utils.trace     import Trace
from utils.decorator import duration

# exclude = {
#     "folder": [".git", ".venv", "__pycache__", "__MACOSX"],
#     "files": ["desktop.ini"]
# }

@duration("{__name__} '{0}'")
def get_filepaths_all( path: Path, exclude: dict = None ) -> Tuple[list, list, list]:
    Trace.action(f"path '{path}'")

    files   = []
    folders = []
    errors  = []

    def get_filepaths( path: Path ) -> None:
        nonlocal files, folders, errors

        try:
            for entry in path.iterdir():
                if entry.is_file():
                    if exclude is None or entry.name not in exclude["files"]:
                        files.append( entry.name )
                elif entry.is_dir():
                    if exclude is None or entry.name not in exclude["folder"]:
                        folders.append( path.as_posix() )
                        get_filepaths( entry )

        except PermissionError as err:
            errors.append( path.as_posix() )
            Trace.error( err )

        except NotADirectoryError as err: # symlink
            errors.append( path.as_posix() )
            Trace.error( err )

    get_filepaths( path )

    Trace.result(f"folders: {len(folders)}, files: {len(files)}, errors: {len(errors)} - exclude: {exclude}")
    return (files, folders, errors)

@duration("{__name__} '{0}'")
def get_filepaths_ancor( ancor_path: Path, exclude: dict = None ) -> Tuple[list, list, list]:
    Trace.action(f"ancor '{ancor_path}'")

    files   = []
    folders = []
    errors  = []

    def get_filepaths( rel_path: str ) -> None:
        nonlocal files, folders, errors

        curr_path = ancor_path / rel_path

        try:
            for entry in Path(curr_path).iterdir():
                if rel_path == "":
                    name = entry.name
                else:
                    name = rel_path + "/" + entry.name # as posix

                if entry.is_file():
                    if exclude is None or entry.name not in exclude["files"]:
                        files.append( name )
                elif entry.is_dir():
                    if exclude is None or entry.name not in exclude["folder"]:
                        folders.append( name )
                        get_filepaths( name )

        except PermissionError as err:
            errors.append( Path(curr_path).as_posix() )
            Trace.error( err )

        except NotADirectoryError as err: # symlink
            errors.append( Path(curr_path).as_posix() )
            Trace.error( err )

    get_filepaths("")

    if len(errors)>0:
        Trace.error(f"errors: {errors}")

    Trace.result(f"folders: {len(folders)}, files: {len(files)}, errors: {len(errors)} - exclude: {exclude}")
    return (files, folders, errors)
