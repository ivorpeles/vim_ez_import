import os
from subprocess import check_output, Popen, PIPE
from tempfile import TemporaryFile
import vim


def _get_imports():
    js_files = []
    for path, dirs, files in os.walk(
        check_output(["git", "rev-parse", "--show-toplevel"]).strip()
    ):
        # modify in place to make os walk skip dirs
        dirs[:] = [d for d in dirs if b"node_modules" not in d]

        js_files += [os.path.join(path, f) for f in files if b".js" in f[-4:]]

    import_lines = []
    for file_ in js_files:
        with open(file_, "r+") as f:
            import_lines += filter(lambda l: l.startswith("import"), f.readlines())

    return list(set(import_lines))


def search_js_imports():
    with TemporaryFile(mode="w+") as imports_file:
        imports_file.writelines(_get_imports())
        imports_file.seek(0)

        with Popen("fzf", stdin=imports_file, stdout=PIPE) as fzf_proc:
            selected_import = fzf_proc.communicate()[0].strip()

    vim.current.buffer[:] = [selected_import] + vim.current.buffer[:]

    vim.command("silent !clear")
    vim.command("redraw!")
