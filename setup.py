from setuptools import setup, find_packages

setup(
    name="share-my-repo",
    version="0.1.0",
    author="Hitesh Sachdeva",
    author_email="yhsachdeva9@myseneca.ca",
    description="CLI tool to package git repositories for sharing with LLMs",
    package_dir={"": "src"},  
    py_modules=[
        "cli",
        "main",
        "file_processor",
        "formatter",
        "git_info",
    ],
    python_requires=">=3.7",
    install_requires=[
        "gitpython>=3.1.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "share-my-repo = cli:main"
            ],
        },
            
    )