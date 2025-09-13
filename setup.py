from setuptools import setup, find_packages

setup(
    name="share-my-repo",
    version="0.1.0",
    author="Hitesh Sachdeva",
    author_email="yhsachdeva9@myseneca.ca",
    description="CLI tool to package git repositories for sharing with LLMs",
    packages=find_packages(where="src"),  # look inside src folder
    package_dir={"": "src"},  # tells Python src is root for packages
    python_requires=">=3.7",
    install_requires=[
        "gitpython>=3.1.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "share-my-repo = cli:main",  
        ],
    },
)
