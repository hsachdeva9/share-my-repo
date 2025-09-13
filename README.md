# share-my-repo

**Version:** 0.1.0  
**Author:** Hitesh Sachdeva  
**License:** MIT  

`share-my-repo` is a CLI tool designed to package Git repositories into a format suitable for analysis by Large Language Models (LLMs). It provides a detailed snapshot of the repository, including directory structure, file contents, Git information, and summary statistics.  

---

## Features

- Recursively discover and process files in a repository.
- Filter files based on include/exclude patterns.
- Respect `.gitignore` rules when discovering files.
- Automatically skip binary files and large files.
- Retrieve Git information (commit, branch, author, date) if the directory is a Git repository.
- Generate Markdown, JSON, or YAML output.
- Estimate token count for LLM input.
- Handle single files or multiple repositories at once.
- Optional truncation of large files to avoid overwhelming output.

---

## Installation

Make sure you have **Python 3.7+** installed.

1. Clone the repository:

```bash
git clone https://github.com/yourusername/share-my-repo.git
cd share-my-repo
```

2. Install the package and dependencies:

```bash
pip install .
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
| `--include` | Include files matching a pattern (e.g., `"*.py,*.js"`). |
| `--exclude` | Exclude files matching a pattern (e.g., `"*.log,venv"`). |
| `--max-file-size` | Maximum file size in bytes (default: `16384`). Larger files are truncated. |
| `--format` | Output format: `markdown` (default), `json`, `yaml`. |
| `--tokens` | Show estimated token count for LLM input. |

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

# Repository Context

## Structure
├── README.md
├── setup.py
└── src
├── cli.py
├── file_processor.py
└── ...

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
