import os
from pathlib import Path
from docnsrt.utils import file_utils as fu


def test_get_all_files_in_dir_nonexistent(tmp_path):
    p = tmp_path / "nope"
    assert fu.get_all_files_in_dir(str(p)) == []


def test_get_all_files_in_dir_with_files(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    (d / "a.txt").write_text("x")
    (d / "b.py").write_text("y")
    (d / "sub").mkdir()
    (d / "sub" / "c.md").write_text("z")

    res = fu.get_all_files_in_dir(str(d))
    assert set(res) == {"a.txt", "b.py", "sub"}


def test_get_files_by_pattern_basic(tmp_path):
    start = tmp_path / "start"
    start.mkdir()
    (start / "file1.py").write_text("print(1)")
    (start / "file2.txt").write_text("x")
    (start / "ignore_me.py").write_text("x")
    nested = start / "nested"
    nested.mkdir()
    (nested / "file3.py").write_text("print(3)")

    results = fu.get_files_by_pattern(
        str(start),
        include_patterns=["**/*.py"],
        ignore_patterns=["ignore_me.py"],
        extensions=[".py"],
    )

    rels = {p.relative_to(start).as_posix() for p in results}
    assert rels == {"file1.py", "nested/file3.py"}


def test_get_line_text_offset_spaces_and_bounds(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("    indented\nnoindent\n  two\n")

    # function expects a zero-based line index
    assert fu.get_line_text_offset_spaces(str(f), 0) == 4
    assert fu.get_line_text_offset_spaces(str(f), 1) == 0
    assert fu.get_line_text_offset_spaces(str(f), 2) == 2
    assert fu.get_line_text_offset_spaces(str(f), 10) == -1


def test_read_file_to_string_and_bytes(tmp_path):
    f = tmp_path / "data.bin"
    content = "hello world\n"
    f.write_text(content, encoding="utf8")

    s = fu.read_file_to_string(str(f))
    b = fu.read_file_to_bytes(str(f))

    assert s == content
    assert isinstance(b, (bytes, bytearray))
    # normalize CRLF on Windows to LF for a platform-independent comparison
    assert b.decode("utf8").replace("\r\n", "\n") == content
