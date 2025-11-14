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
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-watch>=4.2.0",
            "pytest-cov>=4.0.0",
            "watchdog>=2.3.0",
            "flake8>=6.0.0",
            "black>=24.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "share-my-repo = cli:main",
        ],
    },
)
