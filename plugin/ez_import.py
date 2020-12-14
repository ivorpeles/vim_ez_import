import re
import os
from subprocess import check_output, Popen, PIPE
from tempfile import TemporaryFile
import vim


def walk_files(file_name_regex=None, ignore_dirs=None):
    ignore_dirs = [".git"] + (ignore_dirs or [])
    for base_path, dirs, files in os.walk(
        check_output(["git", "rev-parse", "--show-toplevel"]).strip()
    ):
        # modify dirs in place to economically avoid directories
        dirs[:] = [dir_ for dir_ in dirs if dir_.decode("utf-8") not in ignore_dirs]

        for file_name in files:
            if (file_name_regex is None) or file_name_regex.match(
                file_name.decode("utf-8")
            ):
                with open(os.path.join(base_path, file_name), "r+") as file_:
                    yield file_


def run_ez_import_search():
    with TemporaryFile(mode="w+") as imports_file:
        imports_file.writelines(get_imports())
        imports_file.seek(0)

        with Popen("fzf", stdin=imports_file, stdout=PIPE) as fzf_proc:
            selected_import = fzf_proc.communicate()[0].strip()

    if selected_import.decode("utf-8") not in vim.current.buffer:
        vim.current.buffer[:] = [selected_import] + vim.current.buffer[:]

    vim.command("silent !clear")
    vim.command("redraw!")


def get_imports():
    filetype = vim.current.buffer.options["filetype"]
    if filetype == b"python":
        return get_python_imports()

    if filetype in [b"javascript", b"javascriptreact"]:
        return get_js_imports()

    raise RuntimeError(
        f"EZ import couldn't recognize current buffer filetype: {filetype}"
    )


def get_python_imports():
    import_lines = set()
    for file_ in walk_files(
        file_name_regex=re.compile(r".+\.py\Z"), ignore_dirs=["build"]
    ):
        for line in file_.readlines():
            if line.startswith("import") or line.startswith("from"):
                import_lines.add(line)

    return list(import_lines)


def get_js_imports():
    import_lines = set()
    for file_ in walk_files(
        file_name_regex=re.compile(r".+.js(x)?\Z"), ignore_dirs=["node_modules"]
    ):
        for line in file_.readlines():
            if line.startswith("import"):
                import_lines.add(line)

    return list(import_lines)
