from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fb-2minutes-storymaker",
    version="0.1.0",
    author="AllensCreations",
    author_email="you@example.com",
    description="Automated storytelling engine for Picture-Book Motion videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AllensCreations/FB-2minutes-Storymaker",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Add runtime dependencies here as modules are implemented
        # Example: "numpy>=1.24.0", "librosa>=0.10.0"
    ],
    extras_require={
        "dev": [
            "mypy>=1.0.0",
            "pyright>=1.1.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fb-storymaker=main:main",
        ],
    },
)
