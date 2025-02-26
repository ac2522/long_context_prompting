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

def should_exclude_content(path, exclusion_patterns=None):
    """
    Check if a directory's content should be excluded but the directory itself shown.
    
    Args:
        path: Path to check
        exclusion_patterns: List of compiled regex patterns
    
    Returns:
        True if the directory's content should be excluded, False otherwise
    """
    if exclusion_patterns is None or not path.is_dir():
        return False
        
    str_path = str(path)
    # Use a trailing slash to match directories specifically
    return any(pattern.search(str_path + "/") for pattern in exclusion_patterns)

def _tree_lines(path, exclusion_patterns, prefix=""):
    lines = []
    try:
        children = sorted(
            path.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower())
        )
        # Exclude unwanted items:
        children = [child for child in children if not should_exclude(child, exclusion_patterns)]
    except PermissionError:
        return [prefix + "└── [Permission Denied]"]

    for idx, child in enumerate(children):
        is_last = (idx == len(children) - 1)
        connector = "└── " if is_last else "├── "
        if child.is_dir():
            lines.append(f"{prefix}{connector}{child.name}/")
            # Only traverse into the directory if its content is not excluded:
            if not (exclusion_patterns and should_exclude_content(child, exclusion_patterns)):
                extension = "    " if is_last else "│   "
                lines.extend(_tree_lines(child, exclusion_patterns, prefix + extension))
        else:
            lines.append(f"{prefix}{connector}{child.name}")
    return lines

def generate_tree_structure(path, exclusion_patterns=None):
    """
    Generate a tree-like visualization of the folder structure.

    Args:
        path (str or Path): The root folder path.
        exclusion_patterns (list, optional): List of regex patterns for files/folders to exclude.

    Returns:
        str: A string representation of the tree.
    """
    path = Path(path)
    # Start with the root (printed without any connector):
    lines = [f"{path.name}/"]
    lines.extend(_tree_lines(path, exclusion_patterns, ""))
    return "\n".join(lines)

def confirm_processing(folder_path, exclusion_patterns=None, skip_confirm=False):
    """
    Display the folder structure and ask for confirmation before processing.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
        skip_confirm: Whether to skip the confirmation step
    
    Returns:
        Tuple of (boolean indicating whether to proceed, updated exclusion patterns)
    """
    if skip_confirm:
        return True, exclusion_patterns
    
    # Show tree structure
    tree = generate_tree_structure(folder_path, exclusion_patterns)
    print("Project Structure:")
    print(tree)
    
    # Ask for confirmation
    while True:
        response = input("Process these files? (y/n, or specify additional exclusions with 'exclude: pattern1 pattern2'): ").strip().lower()
        if response == 'y':
            return True, exclusion_patterns
        elif response == 'n':
            return False, exclusion_patterns
        elif response.startswith('exclude:'):
            # Handle adding exclusions
            new_exclusions = response[8:].strip().split()
            print(f"Adding exclusions: {new_exclusions}")
            
            # Compile new patterns
            if exclusion_patterns is None:
                exclusion_patterns = []
            for pattern in new_exclusions:
                exclusion_patterns.append(re.compile(pattern))
            
            # Reshow the tree with updated exclusions
            tree = generate_tree_structure(folder_path, exclusion_patterns)
            print("\nUpdated Project Structure:")
            print(tree)
        else:
            print("Please enter 'y' to proceed, 'n' to abort, or 'exclude: pattern1 pattern2' to add exclusions.")

def format_xml(folder_path, exclusion_patterns=None, include_structure=True):
    """
    Generate an XML-formatted representation of the folder structure and file contents.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
        include_structure: Whether to include the folder structure
    
    Returns:
        XML string representation
    """
    folder_path = Path(folder_path).resolve()
    result = ""
    
    if include_structure:
        result += "<folder_structure>\n"
        result += generate_tree_structure(folder_path, exclusion_patterns)
        result += "</folder_structure>\n"
    
    # Now add the documents section
    result += "<documents>\n"
    document_index = 1
    
    # Add file contents for each text file
    for root, dirs, files in os.walk(folder_path):
        root_path = Path(root)
        
        # Skip processing contents of excluded directories
        dirs[:] = [d for d in dirs if not should_exclude_content(root_path / d, exclusion_patterns)]
        
        for file in sorted(files):
            file_path = root_path / file
            
            if should_exclude(file_path, exclusion_patterns):
                continue
                
            if is_text_file(file_path):
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
                document_index += 1
    
    result += "</documents>"
    return result

def format_json(folder_path, exclusion_patterns=None, include_structure=True):
    """
    Generate a JSON-formatted representation of the folder structure and file contents.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
        include_structure: Whether to include the folder structure
    
    Returns:
        JSON string representation
    """
    folder_path = Path(folder_path).resolve()
    
    # Structure to hold the result
    result = {
        "documents": []
    }
    
    if include_structure:
        result["folder_structure"] = generate_tree_structure(folder_path, exclusion_patterns)
    
    # Add file contents
    doc_index = 1
    
    for root, dirs, files in os.walk(folder_path):
        root_path = Path(root)
        
        # Skip processing contents of excluded directories
        dirs[:] = [d for d in dirs if not should_exclude_content(root_path / d, exclusion_patterns)]
        
        for file in sorted(files):
            file_path = root_path / file
            
            if should_exclude(file_path, exclusion_patterns):
                continue
                
            if is_text_file(file_path):
                rel_path = str(file_path.relative_to(folder_path))
                
                result["documents"].append({
                    "index": doc_index,
                    "source": rel_path,
                    "document_content": read_file_content(file_path)
                })
                doc_index += 1
    
    return json.dumps(result, indent=2)

def format_markdown(folder_path, exclusion_patterns=None, include_structure=True):
    """
    Generate a Markdown-formatted representation of the folder structure and file contents.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
        include_structure: Whether to include the folder structure
    
    Returns:
        Markdown string representation
    """
    folder_path = Path(folder_path).resolve()
    result = ""
    
    if include_structure:
        result += "# Project Structure\n\n```\n"
        result += generate_tree_structure(folder_path, exclusion_patterns)
        result += "```\n\n"
    
    result += "# File Contents\n\n"
    
    # Add file contents
    for root, dirs, files in os.walk(folder_path):
        root_path = Path(root)
        
        # Skip processing contents of excluded directories
        dirs[:] = [d for d in dirs if not should_exclude_content(root_path / d, exclusion_patterns)]
        
        for file in sorted(files):
            file_path = root_path / file
            
            if should_exclude(file_path, exclusion_patterns):
                continue
                
            if is_text_file(file_path):
                rel_path = file_path.relative_to(folder_path)
                content = read_file_content(file_path)
                
                result += f"## {rel_path}\n\n"
                
                # Add syntax highlighting using file extension
                ext = file_path.suffix.lstrip('.')
                result += f"```{ext}\n{content}\n```\n\n"
    
    return result

def format_for_llm(folder_path, exclusion_patterns=None, llm_type="claude", include_structure=True):
    """
    Generate the appropriate output format based on the LLM type.
    
    Args:
        folder_path: Path to the folder to process
        exclusion_patterns: List of regex patterns for files/folders to exclude
        llm_type: Target LLM format (claude, gemini, openai)
        include_structure: Whether to include the folder structure in the output
    
    Returns:
        Formatted string for the specified LLM
    """
    folder_path = Path(folder_path).resolve()
    result = ""
    
    # Add folder structure if requested
    if include_structure:
        if llm_type == "claude":
            result += "<folder_structure>\n"
            result += generate_tree_structure(folder_path, exclusion_patterns)
            result += "</folder_structure>\n\n"
        else:  # gemini or openai
            result += "Project Structure:\n```\n"
            result += generate_tree_structure(folder_path, exclusion_patterns)
            result += "```\n\n"
    
    # Add file contents
    if llm_type == "claude":
        result += "<documents>\n"
        document_index = 1
        
        for root, dirs, files in os.walk(folder_path):
            root_path = Path(root)
            
            # Skip processing contents of excluded directories
            dirs[:] = [d for d in dirs if not should_exclude_content(root_path / d, exclusion_patterns)]
            
            for file in sorted(files):
                file_path = root_path / file
                
                if should_exclude(file_path, exclusion_patterns):
                    continue
                    
                if is_text_file(file_path):
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
                    document_index += 1
        
        result += "</documents>"
    else:  # gemini or openai
        for root, dirs, files in os.walk(folder_path):
            root_path = Path(root)
            
            # Skip processing contents of excluded directories
            dirs[:] = [d for d in dirs if not should_exclude_content(root_path / d, exclusion_patterns)]
            
            for file in sorted(files):
                file_path = root_path / file
                
                if should_exclude(file_path, exclusion_patterns):
                    continue
                    
                if is_text_file(file_path):
                    rel_path = file_path.relative_to(folder_path)
                    content = read_file_content(file_path)
                    
                    result += f"{folder_path.name}/{rel_path}\n"
                    result += "---\n"
                    result += f"{content}\n"
                    result += "---\n"
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description="Convert folder structure to LLM prompt format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  folder-to-llm /path/to/folder                    # Basic usage with Claude XML output
  folder-to-llm /path/to/folder -l openai          # Format for OpenAI models
  folder-to-llm /path/to/folder -s                 # Skip outputting folder structure
  folder-to-llm /path/to/folder -y                 # Skip confirmation step
  folder-to-llm /path/to/folder -e "node_modules/" ".git/"  # Show directories but exclude contents
  folder-to-llm /path/to/folder -o output.txt      # Save to file
        """
    )
    
    parser.add_argument("folder_path", help="Path to the folder to process")
    parser.add_argument(
        "--exclude", "-e", 
        nargs="+", 
        help="Patterns to exclude (add '/' suffix for directory exclusion with structure preservation)"
    )
    parser.add_argument(
        "--format", "-f", 
        choices=["xml", "json", "markdown"], 
        default="xml",
        help="Output format type (default: xml) - only used with Claude format"
    )
    parser.add_argument(
        "--llm", "-l", 
        choices=["claude", "gemini", "openai"], 
        default="claude",
        help="Target LLM format (default: claude)"
    )
    parser.add_argument(
        "--skip-structure", "-s", 
        action="store_true", 
        help="Skip outputting the folder structure"
    )
    parser.add_argument(
        "--no-confirm", "-y", 
        action="store_true", 
        help="Skip confirmation step"
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
    
    # Confirm processing (if not skipped)
    if not args.no_confirm:
        proceed, exclusion_patterns = confirm_processing(folder_path, exclusion_patterns, args.no_confirm)
        if not proceed:
            print("Operation cancelled.")
            sys.exit(0)
    
    # Generate the output based on format and LLM type
    if args.llm == "claude":
        if args.format == "xml":
            result = format_xml(folder_path, exclusion_patterns, not args.skip_structure)
        elif args.format == "json":
            result = format_json(folder_path, exclusion_patterns, not args.skip_structure)
        elif args.format == "markdown":
            result = format_markdown(folder_path, exclusion_patterns, not args.skip_structure)
    else:
        # Use the LLM-specific formatter for gemini/openai
        result = format_for_llm(
            folder_path, 
            exclusion_patterns, 
            args.llm, 
            not args.skip_structure
        )
    
    # Output the result
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Output written to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
