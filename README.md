# Folder-to-LLM

A Python utility that converts folder structures and file contents into LLM-friendly prompt formats.

## Features

- Recursively scans folder structures
- Includes file contents for all readable text files
- Supports multiple output formats (XML, JSON, Markdown)
- Excludes binary/non-readable files from content extraction
- Allows pattern-based exclusion of files and folders
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

# Exclude specific files or folders (supports regex patterns)
folder-to-llm /path/to/your/folder --exclude "node_modules" ".git" "*.log"

# Save output to a file
folder-to-llm /path/to/your/folder --output result.txt
folder-to-llm /path/to/your/folder -o result.txt

# Show help
folder-to-llm --help
```

### Example Output

#### XML format
```xml
<documents>
  <document index="1">
    <source>folder_structure</source>
    <document_content>
      project/
        src/
          main.py
          utils.py
        README.md
    </document_content>
  </document>
  <document index="2">
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
  "documents": [
    {
      "index": 1,
      "source": "folder_structure",
      "document_content": "project/\n  src/\n    main.py\n    utils.py\n  README.md"
    },
    {
      "index": 2,
      "source": "src/main.py",
      "document_content": "# Main application code here"
    }
  ]
}
```

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
