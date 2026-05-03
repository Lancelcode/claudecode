from pathlib import Path
from claudecode.tools import read_file, write_file, list_dir, execute



def test_write_and_read_file(tmp_path):
    file_path = tmp_path / "test.txt"

    # Write
    result = write_file(str(file_path), "hello world")
    assert "Successfully wrote" in result

    # Read
    content = read_file(str(file_path))
    assert content == "hello world"


def test_read_file_not_found():
    result = read_file("non_existent.txt")
    assert "Error: file not found" in result


def test_list_dir(tmp_path):
    # Create files
    (tmp_path / "a.txt").write_text("A")
    (tmp_path / "b.txt").write_text("B")

    result = list_dir(str(tmp_path))

    assert "a.txt" in result
    assert "b.txt" in result


def test_list_dir_not_found():
    result = list_dir("non_existent_dir")
    assert "Error: directory not found" in result


def test_execute_unknown_tool():
    from claudecode.tools import execute  # ← change this too
    result = execute("unknown", {})
    assert "unknown tool" in result
