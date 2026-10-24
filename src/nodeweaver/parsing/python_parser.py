from dataclasses import dataclass
from pathlib import Path
import tree_sitter
import tree_sitter_python

@dataclass
class ParseResult:
    """Holds the syntax tree and the source bytes used to generate it."""
    tree: tree_sitter.Tree
    source_bytes: bytes

    @property
    def has_error(self) -> bool:
        """Returns True if the parser encountered a syntax error."""
        return self.tree.root_node.has_error

def parse_file(path: str | Path) -> ParseResult:
    """
    Reads a Python file as bytes and parses it into a tree-sitter syntax tree.
    
    Args:
        path: Path to the Python file.
        
    Returns:
        ParseResult containing the syntax tree and the raw source bytes.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there are permission issues reading the file.
    """
    file_path = Path(path)
    
    # Read the file as raw bytes. We let exceptions bubble up to the caller.
    source_bytes = file_path.read_bytes()
    
    # Initialize the parser with the Python grammar
    python_lang = tree_sitter.Language(tree_sitter_python.language())
    parser = tree_sitter.Parser(python_lang)
    
    # Parse the bytes into a syntax tree
    tree = parser.parse(source_bytes)
    
    return ParseResult(tree=tree, source_bytes=source_bytes)