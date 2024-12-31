"""
    © Jürgen Schoenemeyer, 31.12.2024

    PUBLIC:
     - get_filepaths_all( path: Path ) -> list:
     - get_filepaths_ancor( ancor_path: Path ) -> list:

"""

from pathlib import Path

from utils.trace     import Trace
from utils.decorator import duration

@duration("{__name__} '{0}'")
def get_filepaths_all( path: Path ) -> list:
    Trace.action(f"path '{path}'")

    files   = []
    dirs    = []
    errors  = []

    def get_filepaths( path: Path ) -> None:
        nonlocal files, dirs, errors

        try:
            for entry in path.iterdir():
                if entry.is_file():
                    files.append( entry )
                elif entry.is_dir():
                    dirs.append( path )
                    get_filepaths( entry )

        except PermissionError as err:
            errors.append( path.as_posix() )
            Trace.error( err )

        except NotADirectoryError as err: # symlink
            errors.append( path.as_posix() )
            Trace.error( err )

    get_filepaths( path )

    Trace.result(f"dirs: {len(dirs)}, files: {len(files)}, errors: {len(errors)}")
    return (files, errors)

@duration("{__name__} '{0}'")
def get_filepaths_ancor( ancor_path: Path ) -> list:
    Trace.action(f"ancor '{ancor_path}'")

    files   = []
    dirs    = []
    errors  = []

    def get_filepaths( rel_path: str ) -> None:
        nonlocal files, dirs, errors

        curr_path = ancor_path / rel_path

        try:
            for entry in Path(curr_path).iterdir():
                if rel_path == "":
                    name = str(entry.name)
                else:
                    name = rel_path + "/" + str(entry.name)

                if entry.is_file():
                    files.append( name )
                elif entry.is_dir():
                    dirs.append( name )
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

    Trace.result(f"dirs: {len(dirs)}, files: {len(files)}, errors: {len(errors)}")
    return (files, dirs, errors)
