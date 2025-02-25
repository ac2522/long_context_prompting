#!/usr/bin/env python3

import os
import argparse
import mimetypes
from pathlib import Path
import sys
import re
import json
from importlib import metadata
# Initialize mimetypes
mimetypes.init()

def is_text_file(file_path):
    """
    Check if a file is text-based (readable).
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if the file is text-based, False if binary
    """
    # Known text file extensions
    text_extensions = {
        '.py', '.txt', '.json', '.csv', '.md', '.html', '.css', '.js', 
        '.cpp', '.c', '.h', '.hpp', '.java', '.xml', '.yml', '.yaml', '.sh', 
        '.bat', '.ps1', '.tex', '.ini', '.cfg', '.conf', '.jsx', '.ts',
        '.tsx', '.sql', '.php', '.rb', '.rs', '.go', '.dart', '.swift',
        '.ipynb', '.tex', '.log', '.env', '.gitignore', '.toml'
    }
    
    # Check file extension
    suffix = Path(file_path).suffix.lower()
    if suffix in text_extensions:
        return True
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('text/'):
        return True
    
    # If still unsure, check file content for binary data
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(4096)
            # Binary files often contain null bytes
            if b'\x00' in chunk:
                return False
            # Check if most of the content is ASCII
            non_ascii = sum(1 for b in chunk if b > 127)
            if len(chunk) > 0 and non_ascii > len(chunk) * 0.3:
                return False
            return True
    except Exception:
        # If we can't read it, consider it binary
        return False

def read_file_content(file_path):
    """
    Read the content of a text file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Content of the file as a string, or error message
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def format_xml(folder_path, exclusion_patterns=None):
    """
    Generate an XML-formatted representation of the folder structure and file contents.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
    
    Returns:
        XML string representation
    """
    folder_path = Path(folder_path).resolve()
    result = "<documents>\n"
    document_index = 1
    
    # First document: folder structure
    result += f"  <document index=\"{document_index}\">\n"
    result += f"    <source>folder_structure</source>\n"
    result += f"    <document_content>\n"
    
    def build_folder_structure(path, indent=0):
        if should_exclude(path):
            return ""
            
        structure = " " * 6 + " " * indent + f"{path.name}/\n"
        
        try:
            # Sort: directories first, then files, both alphabetically
            items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            
            for item in items:
                if should_exclude(item):
                    continue
                    
                if item.is_dir():
                    structure += build_folder_structure(item, indent + 2)
                else:
                    structure += " " * 6 + " " * (indent + 2) + f"{item.name}\n"
        except PermissionError:
            structure += " " * 6 + " " * (indent + 2) + "[Permission denied]\n"
        
        return structure
    
    result += build_folder_structure(folder_path)
    result += "    </document_content>\n"
    result += "  </document>\n"
    
    # Add file contents for each text file
    for root, dirs, files in os.walk(folder_path):
        # Process directories in-place to respect excludes
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for file in sorted(files):
            file_path = Path(root) / file
            
            if should_exclude(file_path):
                continue
                
            if is_text_file(file_path):
                document_index += 1
                rel_path = file_path.relative_to(folder_path)
                
                result += f"  <document index=\"{document_index}\">\n"
                result += f"    <source>{rel_path}</source>\n"
                result += f"    <document_content>\n"
                
                content = read_file_content(file_path)
                # Add indentation to each line for XML formatting
                indented_content = "\n".join(" " * 6 + line for line in content.splitlines())
                if indented_content:
                    result += indented_content + "\n"
                
                result += "    </document_content>\n"
                result += "  </document>\n"
    
    result += "</documents>"
    return result

def format_json(folder_path, exclusion_patterns=None):
    """
    Generate a JSON-formatted representation of the folder structure and file contents.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
    
    Returns:
        JSON string representation
    """
    folder_path = Path(folder_path).resolve()
    
    # Structure to hold the result
    result = {
        "documents": [
            {
                "index": 1,
                "source": "folder_structure",
                "document_content": ""
            }
        ]
    }
    
    # Build folder structure as a string
    folder_structure = []
    
    def build_folder_structure(path, indent=0):
        if should_exclude(path):
            return
            
        folder_structure.append(" " * indent + f"{path.name}/")
        
        try:
            # Sort: directories first, then files, both alphabetically
            items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            
            for item in items:
                if should_exclude(item):
                    continue
                    
                if item.is_dir():
                    build_folder_structure(item, indent + 2)
                else:
                    folder_structure.append(" " * (indent + 2) + f"{item.name}")
        except PermissionError:
            folder_structure.append(" " * (indent + 2) + "[Permission denied]")
    
    build_folder_structure(folder_path)
    result["documents"][0]["document_content"] = "\n".join(folder_structure)
    
    # Add file contents
    doc_index = 1
    
    for root, dirs, files in os.walk(folder_path):
        # Process directories in-place to respect excludes
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for file in sorted(files):
            file_path = Path(root) / file
            
            if should_exclude(file_path):
                continue
                
            if is_text_file(file_path):
                doc_index += 1
                rel_path = str(file_path.relative_to(folder_path))
                
                result["documents"].append({
                    "index": doc_index,
                    "source": rel_path,
                    "document_content": read_file_content(file_path)
                })
    
    return json.dumps(result, indent=2)

def format_markdown(folder_path, exclusion_patterns=None):
    """
    Generate a Markdown-formatted representation of the folder structure and file contents.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
    
    Returns:
        Markdown string representation
    """
    folder_path = Path(folder_path).resolve()
    result = "# Folder Structure\n\n"
    
    def build_folder_structure(path, indent=0):
        if should_exclude(path):
            return ""
            
        structure = " " * indent + "- **" + path.name + "/**\n"
        
        try:
            # Sort: directories first, then files, both alphabetically
            items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            
            for item in items:
                if should_exclude(item):
                    continue
                    
                if item.is_dir():
                    structure += build_folder_structure(item, indent + 2)
                else:
                    structure += " " * (indent + 2) + "- " + item.name + "\n"
        except PermissionError:
            structure += " " * (indent + 2) + "- [Permission denied]\n"
        
        return structure
    
    result += build_folder_structure(folder_path)
    result += "\n# File Contents\n\n"
    
    # Add file contents
    for root, dirs, files in os.walk(folder_path):
        # Process directories in-place to respect excludes
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for file in sorted(files):
            file_path = Path(root) / file
            
            if should_exclude(file_path):
                continue
                
            if is_text_file(file_path):
                rel_path = file_path.relative_to(folder_path)
                content = read_file_content(file_path)
                
                result += f"## {rel_path}\n\n"
                
                # Add syntax highlighting using file extension
                ext = file_path.suffix.lstrip('.')
                result += f"```{ext}\n{content}\n```\n\n"
    
    return result

def should_exclude(path, exclusion_patterns=None):
    """
    Check if a path should be excluded based on the exclusion patterns.
    
    Args:
        path: Path to check
        exclusion_patterns: List of compiled regex patterns
    
    Returns:
        True if the path should be excluded, False otherwise
    """
    if exclusion_patterns is None:
        return False
        
    str_path = str(path)
    return any(pattern.search(str_path) for pattern in exclusion_patterns)

def main():
    parser = argparse.ArgumentParser(
        description="Convert folder structure to LLM prompt format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  folder-to-llm /path/to/folder                    # Basic usage with XML output
  folder-to-llm /path/to/folder -f markdown        # Output in Markdown format
  folder-to-llm /path/to/folder -e "node_modules" ".git"  # Exclude directories
  folder-to-llm /path/to/folder -o output.txt      # Save to file
        """
    )
    
    parser.add_argument("folder_path", help="Path to the folder to process")
    parser.add_argument(
        "--exclude", "-e", 
        nargs="+", 
        help="Patterns to exclude (file/folder names or regexes)"
    )
    parser.add_argument(
        "--format", "-f", 
        choices=["xml", "json", "markdown"], 
        default="xml",
        help="Output format type (default: xml)"
    )
    parser.add_argument(
        "--output", "-o", 
        help="Output file (default: print to stdout)"
    )
    parser.add_argument(
        "--version", "-v", 
        action="version", 
        version=f"%(prog)s {metadata.version('folder-to-llm')}"
    )
    
    args = parser.parse_args()
    
    # Validate folder path
    folder_path = Path(args.folder_path)
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    # Compile exclusion patterns
    exclusion_patterns = None
    if args.exclude:
        exclusion_patterns = [re.compile(pattern) for pattern in args.exclude]
    
    # Format the output based on the selected format
    if args.format == "xml":
        result = format_xml(folder_path, exclusion_patterns)
    elif args.format == "json":
        result = format_json(folder_path, exclusion_patterns)
    elif args.format == "markdown":
        result = format_markdown(folder_path, exclusion_patterns)
    
    # Output the result
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Output written to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
