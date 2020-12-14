let _ez_import_py_utils_path = expand("<sfile>:p:h") . "/ez_import.py"

function InitEzImport()
    execute ':py3file ' . g:_ez_import_py_utils_path
endfunction

function GetEzImport()
    python3 run_ez_import_search()
endfunction
