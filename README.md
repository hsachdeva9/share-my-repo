# share-my-repo

**Version:** 0.1.0  
**Author:** Hitesh Sachdeva  
**License:** MIT  

`share-my-repo` is a CLI tool designed to package Git repositories into a format suitable for analysis by Large Language Models (LLMs). It provides a detailed snapshot of the repository, including directory structure, file contents, Git information, and summary statistics.  

---

## Features

### **File Discovery & Processing**
- **Recursive file discovery** - Automatically finds and processes all files in a repository
- **Smart file filtering** - Skip binary files, large files, and unwanted directories
- **Multiple repository support** - Handle single files or multiple repositories at once
- **Line numbers in output** - Optionally include line numbers for all file contents

### **Directory Structure**
- **Visual tree representation** - Generates clear, easy-to-read directory trees
- **Organized file listing** - Shows the complete organization of all included files

### **Advanced Filtering**
- **Pattern-based filtering** - Include/exclude files using glob patterns (`*.py`, `*.js`, etc.)
- **Recent changes filter** - Show only files modified in the last 7 days with `--recent` flag
- **File size limits** - Optional truncation of large files to avoid overwhelming output
- **Preview feature** - Limit the number of lines shown per file with `--preview <N>`. Useful for quickly inspecting file content without printing full files.


### **Git Integration**
- **Repository metadata** - Retrieve commit hash, branch, author, and date information
- **Git-aware processing** - Automatically detects and processes Git repositories

### **Output Formats & Analysis**
- **Multiple output formats** - Generate Markdown, JSON, or YAML output
- **Token estimation** - Estimate token count for LLM input optimization
- **Summary statistics** - File counts, line counts, and other useful metrics
- **TOML configuration file support** - Store commonly used options in a project-level config file

---

## Installation

Make sure you have **Python 3.7+** installed.

1. Clone the repository:

### For End Users
Clone and install the package:

```bash
# clone the repository 
git clone https://github.com/yourusername/share-my-repo.git
cd share-my-repo

# install dependencies
pip install .
```
## For Development / Contributors

Install in editable mode to make code changes without reinstalling:

```bash
# clone the repository 
git clone https://github.com/yourusername/share-my-repo.git
cd share-my-repo

# install dependencies
pip install -e .
```

Dependencies:

- gitpython>=3.1.0

- click>=8.0.0

- pyyaml (for YAML output)

---

## Usage

```bash
share-my-repo [OPTIONS] [PATHS...]
```
### Options 

| Option | Description |
|--------|-------------|
| `-o, --output <file>` | Path to save the output file. If omitted, output is printed to console. |
| `-v, --version` | Show the version of the tool. |
| `-h, --help` | Show help message and exit. |
| `--include` | Include files matching a pattern (e.g., `"*.py,*.js"`). |
| `--exclude` | Exclude files matching a pattern (e.g., `"*.log,venv"`). |
| `--max-file-size` | Maximum file size in bytes (default: `16384`). Larger files are truncated. |
| `--format` | Output format: `markdown` (default), `json`, `yaml`. |
| `--tokens` | Show estimated token count for LLM input. |
| `-r, --recent` | Include only files modified in the last 7 days. Shows modification dates in output. |
| `-l, --line-numbers` | Include line numbers for file content in output.. |
| `--preview` | Limit the number of lines displayed per file. Useful to avoid printing full file content. |

## Examples

### Process the current directory and print Markdown to console:

```bash
share-my-repo .
```

### Process a repository and save output to a file:

```bash
share-my-repo . --output repo_context.md
```

### Include only Python and JavaScript files:

```bash
share-my-repo . --include "*.py,*.js"
```

### Output as JSON:
```bash
share-my-repo . --format json --output repo.json
```

### Show only recently modified files (last 7 days):
```bash
share-my-repo . --recent
```

### Show recent changes and save to file:
```bash
share-my-repo . --recent --output recent_changes.md
```

### Combine recent filter with other options:
```bash
share-my-repo . --recent --include "*.py" --format json
```
### Include line numbers in file contents:
```bash
share-my-repo . --line-numbers
share-my-repo . -l
```
### Preview the first 5 lines of each file:
```bash
share-my-repo . --preview 5
```
### Preview the first 10 lines of a specific folder or file:
```bash
share-my-repo src --preview 10
share-my-repo README.md --preview 10
```

---

## Configuration via TOML

You can store commonly used options in a project-level TOML configuration file so you don't have to pass the same flags every time.

**Supported filenames (place in the repository root):**
- .share-my-repo-config.toml
- .share-my-repo.toml

**Behavior:**
- If a supported TOML config file exists in the current working directory, share-my-repo will load the file and use the values as defaults.
- CLI arguments always take precedence — any option you pass on the command line overrides the value from the TOML file.
- Unknown keys in the TOML file are ignored (this makes it safe to add future options).
- If the TOML file exists but cannot be parsed, the program will exit with an error message.

**Supported options in TOML (examples):**
- output (string) — path to write output
- format (string) — markdown, json, or yaml
- include / exclude — either a single CSV string (e.g., "\*.py,\*.js") or an array of strings (e.g., ["*.py","*.md"])
- max_file_size (integer) — bytes before truncation
- tokens, recent, line_numbers (boolean)
- preview (integer) — number of lines to show per file

**Configuration with TOML**
You can also create a `.share-my-repo-config.toml` file in the root of your repository to avoid typing the same flags every time.  
By default, this file is optional and empty, but you can uncomment and edit the keys to customize the behavior.  

**Example** `.share-my-repo-config.toml:`
```bash
output = "output.txt"
include = "*.js"
exclude = "*test*"
max_file_size = 1024
format = "json"
# etc...
```

**Parser note:** the tool tries to use Python 3.11's built-in tomllib first; when running under older Python versions it falls back to the tomli package. If you are using Python < 3.11, install the fallback with:
```bash
pip install tomli
```

**Running:**
```bash
# Process the current directory 
share-my-repo .

# Save output to a file
share-my-repo . --output repo_context.md

# Change output format 
share-my-repo . --format json --output repo.json
share-my-repo . --format yaml --output repo.yaml

# Include only certain files
share-my-repo . --include "*.py,*.js"
```

---

## Structure

```bash
share-my-repo/
├── README.md
├── setup.py
├── LICENSE
├── .gitignore
└── src/
    ├── cli.py
    ├── file_processor.py
    ├── formatter.py
    ├── git_info.py
    ├── main.py
    └── __init__.py
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m "Add feature"`.
4. Push to your branch: `git push origin feature-name`.
5. Open a Pull Request.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
