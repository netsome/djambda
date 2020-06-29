import argparse
import compileall
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import zipapp
from distutils import dir_util
from fnmatch import fnmatchcase


def _build_filter(*patterns):
    """
    Given a list of patterns, return a callable that will be true only if
    the input matches at least one of the patterns.
    """
    return lambda name: any(fnmatchcase(name, pat=pat) for pat in patterns)


def build_filter(exclude=(), include=("*",)):
    exclude_filter = _build_filter(*exclude)
    include_filter = _build_filter(*include)
    return lambda path: include_filter(path.as_posix()) and not exclude_filter(
        path.as_posix()
    )


def build(args):
    temp_dir = tempfile.mkdtemp()
    dir_util.copy_tree(args.source, temp_dir)
    # install requirements
    for requirements in args.requirements:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                requirements,
                "--target",
                temp_dir,
            ]
        )
    # create staticfiles manifest
    if args.collect_manifest:
        static_dir = tempfile.mkdtemp()
        subprocess.check_call(
            [sys.executable, os.path.join(temp_dir, "manage.py"), "collectstatic",],
            env={"ENABLE_MANIFEST_STORAGE": "True", "STATIC_ROOT": static_dir},
        )
        shutil.copy2(os.path.join(static_dir, "staticfiles.json"), temp_dir)
        shutil.rmtree(static_dir)
    # create pyc files
    compileall.compile_dir(
        temp_dir,
        legacy=True,
        invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
        quiet=args.quiet,
    )
    # zip app
    zipapp.create_archive(
        temp_dir,
        args.output,
        interpreter=args.python,
        main=args.main,
        compressed=args.compress,
        filter=build_filter(args.exclude, args.include),
    )
    shutil.rmtree(temp_dir)


def main(args=None):
    """Build django application.

    The ARGS parameter lets you specify the argument list directly.
    Omitting ARGS (or setting it to None) works as for argparse, using
    sys.argv[1:] as the argument list.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--requirements",
        "-r",
        default=[],
        nargs="*",
        help="Install from the given requirements file. "
        "This option can be used multiple times.",
    )
    parser.add_argument(
        "--collect_manifest", action="store_true",
    )
    parser.add_argument(
        "-q",
        action="count",
        dest="quiet",
        default=0,
        help="output only error messages; -qq will suppress "
        "the error messages as well.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="The name of the output archive. Required if SOURCE is an archive.",
    )
    parser.add_argument(
        "--python",
        "-p",
        default=None,
        help="The name of the Python interpreter to use (default: no shebang line).",
    )
    parser.add_argument(
        "--main",
        "-m",
        default=None,
        help="The main function of the application "
        "(default: use an existing __main__.py).",
    )
    parser.add_argument(
        "--compress",
        "-c",
        action="store_true",
        help="Compress files with the deflate method. "
        "Files are stored uncompressed by default.",
    )
    parser.add_argument("source", help="Source directory (or existing archive).")
    parser.add_argument(
        "--include",
        "-i",
        default=["*"],
        nargs="*",
        help="A glob-style sequence of paths to include.",
    )
    parser.add_argument(
        "--exclude",
        "-e",
        default=[],
        nargs="*",
        help="A glob-style sequence of paths to exclude.",
    )

    args = parser.parse_args(args)

    if os.path.isfile(args.source):
        if args.output is None or (
            os.path.exists(args.output) and os.path.samefile(args.source, args.output)
        ):
            raise SystemExit("In-place editing of archives is not supported")
        if args.main:
            raise SystemExit("Cannot change the main function when copying")

    build(args)


if __name__ == "__main__":
    main()
