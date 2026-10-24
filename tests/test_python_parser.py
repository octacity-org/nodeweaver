from pathlib import Path
import pytest
from nodeweaver.parsing.python_parser import parse_file

# We locate the path to the 'examples' folder in the project's root directory
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

def test_parse_valid_file():
    """Test that a valid Python file parses correctly and the root is a module."""
    # We are using the file examples/sample_basic/main.py
    valid_file_path = EXAMPLES_DIR / "sample_basic" / "main.py"
    
    result = parse_file(valid_file_path)
    
    assert not result.has_error, "Valid file should not have parsing errors"
    assert result.tree.root_node.type == "module", "Root node of a Python file should be 'module'"
    assert len(result.source_bytes) > 0, "Source bytes should not be empty"

def test_parse_broken_file():
    """Test that a file with syntax errors doesn't crash the parser and reports the error."""
    # We are using the file examples/sample_broken/broken.py
    broken_file_path = EXAMPLES_DIR / "sample_broken" / "broken.py"
    
    result = parse_file(broken_file_path)
    
    # The parser should not crash and should return `has_error = True`
    assert result.has_error, "Parser should flag the syntax error"
    assert result.tree.root_node.type == "module", "Root node should still be 'module' even with errors"

def test_missing_file_raises(tmp_path):
    """Test that parsing a non-existent file raises a FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        parse_file(tmp_path / "missing.py")

def test_valid_functions_survive_a_syntax_error():
    """Test that valid function definitions can still be extracted even if the file has syntax errors."""
    result = parse_file(EXAMPLES_DIR / "sample_broken" / "broken.py")
    names = {
        node.child_by_field_name("name").text.decode()
        for node in result.tree.root_node.children
        if node.type == "function_definition" and not node.has_error
    }
    assert names == {"valid_function", "another_valid_function"}