from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="cgmerger",
    version="0.1.0",
    description="CodinGame Merger (merges files from a folder "
    "into one file served by Coding Game web plugin)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ajakubo1/CGMerger",
    author="Adam Jakubowski",
    author_email="ajakubo1@gmail.com",  # Optional
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="codingame, merge",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.5, <4",
    install_requires=["chardet>=3.0.4,<4.0.0"],
    extras_require={"dev": ["check-manifest"], "test": ["coverage"],},
    entry_points={"console_scripts": ["cgmerger=cgmerger.cgmerge:main",],},
    project_urls={
        "Bug Reports": "https://github.com/ajakubo1/CGMerger/issues",
        "Source": "https://github.com/ajakubo1/CGMerger/",
    },
)
