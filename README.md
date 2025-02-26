# Folder-to-LLM

A Python utility that converts folder structures and file contents into LLM-friendly prompt formats.

## Features

- Recursively scans folder structures
- Includes file contents for all readable text files
- Supports multiple output formats (XML, JSON, Markdown)
- Interactive confirmation step to review files
- Tree-style visualization of folder structure
- Support for multiple LLM formats (Claude, OpenAI/ChatGPT, Gemini)
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
# Basic usage - outputs Claude XML format to stdout
folder-to-llm /path/to/your/folder

# Specify output format for Claude (XML, JSON, or Markdown)
folder-to-llm /path/to/your/folder --format json
folder-to-llm /path/to/your/folder -f markdown

# Target different LLM formats
folder-to-llm /path/to/your/folder --llm openai
folder-to-llm /path/to/your/folder -l gemini

# Skip outputting folder structure
folder-to-llm /path/to/your/folder --skip-structure
folder-to-llm /path/to/your/folder -s

# Skip the confirmation step
folder-to-llm /path/to/your/folder --no-confirm
folder-to-llm /path/to/your/folder -y

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

## Interactive Confirmation

By default, the tool will show you the folder structure and ask for confirmation before processing:

```
Project Structure:
my_directory/
├── file1.txt
├── file2.txt
├── .hidden_file.txt
├── temp.log
└── subdirectory/
    └── file3.txt

Process these files? (y/n, or specify additional exclusions with 'exclude: pattern1 pattern2'):
```

You can:
- Enter `y` to proceed
- Enter `n` to cancel
- Enter `exclude: pattern1 pattern2` to add more exclusions and update the view

## Example Output Formats

### Claude format (XML)
```xml
<folder_structure>
my_directory/
├── file1.txt
├── file2.txt
├── .hidden_file.txt
├── temp.log
└── subdirectory/
    └── file3.txt
</folder_structure>
<documents>
  <document index="1">
    <source>file1.txt</source>
    <document_content>
      Contents of file1.txt
    </document_content>
  </document>
  <!-- Additional files would be listed here -->
</documents>
```

### OpenAI/Gemini format
```
Project Structure:
```
my_directory/
├── file1.txt
├── file2.txt
├── .hidden_file.txt
├── temp.log
└── subdirectory/
    └── file3.txt
```

my_directory/file1.txt
---
Contents of file1.txt
---
my_directory/file2.txt
---
Contents of file2.txt
---
my_directory/subdirectory/file3.txt
---
Contents of file3.txt
---
```

### JSON format (Claude only)
```json
{
  "folder_structure": "my_directory/\n├── file1.txt\n├── file2.txt\n...",
  "documents": [
    {
      "index": 1,
      "source": "file1.txt",
      "document_content": "Contents of file1.txt"
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
