# Folder-to-LLM

A Python utility that converts folder structures and file contents into LLM-friendly prompt formats.

## Features

- Recursively scans folder structures
- Includes file contents for all readable text files
- Supports multiple output formats (XML, JSON, Markdown)
- Excludes binary/non-readable files from content extraction
- Allows pattern-based exclusion of files and folders
- Special handling for directories: can include in structure but exclude contents
- Works on both Linux and Windows

## Installation

### Ubuntu/Linux

```bash
# Clone the repository
git clone https://github.com/yourusername/long_context_prompting.git
cd long_context_prompting

# Install the package
pip install -e .

# Make the command globally available
chmod +x folder_to_llm.py
```

### Windows

```powershell
# Clone the repository
git clone https://github.com/yourusername/long_context_prompting.git
cd long_context_prompting

# Install the package
pip install -e .
```

## Usage

Once installed, you can use the tool via the command line:

```bash
# Basic usage - outputs XML format to stdout
folder-to-llm /path/to/your/folder

# Specify output format (XML, JSON, or Markdown)
folder-to-llm /path/to/your/folder --format json
folder-to-llm /path/to/your/folder -f markdown

# Exclude specific files or folders
folder-to-llm /path/to/your/folder --exclude "*.log" "temp.txt"

# Exclude directory contents but show directories in structure (note the trailing slash)
folder-to-llm /path/to/your/folder --exclude "node_modules/" ".git/" "venv/"

# Save output to a file
folder-to-llm /path/to/your/folder --output result.txt
folder-to-llm /path/to/your/folder -o result.txt

# Show help
folder-to-llm --help
```

### Example Output

#### XML format
```xml
<folder_structure>
      project/
        src/
          main.py
          utils.py
        venv/
        README.md
</folder_structure>
<documents>
  <document index="1">
    <source>src/main.py</source>
    <document_content>
      # Main application code here
    </document_content>
  </document>
  <!-- Additional files would be listed here -->
</documents>
```

#### JSON format
```json
{
  "folder_structure": "project/\n  src/\n    main.py\n    utils.py\n  venv/\n  README.md",
  "documents": [
    {
      "index": 1,
      "source": "src/main.py",
      "document_content": "# Main application code here"
    }
  ]
}
```

## Directory Exclusion Behavior

- To completely exclude a file or directory: `--exclude "temp.txt" "junk"` 
- To show directory in structure but exclude contents: `--exclude "node_modules/" "venv/"` (note the trailing slash)

## Troubleshooting

### Command not found (Linux)
If the `folder-to-llm` command is not recognized after installation, ensure:
1. The installation directory is in your PATH
2. Try running `pip install -e .` with `--user` flag if you don't have admin privileges

### Command not found (Windows)
For Windows, you may need to:
1. Ensure Python's Scripts directory is in your PATH
2. Try running the command as `python -m folder_to_llm`

## Windows-specific Notes

On Windows systems, you might experience issues with path handling. If you encounter problems:
- Use forward slashes in paths (`/`) or escaped backslashes (`\\`)
- If a path contains spaces, enclose it in quotes: `"C:/My Folder/project"`

## License

MIT
