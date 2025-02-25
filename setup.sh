from setuptools import setup, find_packages

setup(
    name="folder-to-llm",
    version="0.1.0",
    description="Convert folder structure to LLM prompt format",
    author="Your Name",
    packages=find_packages(),
    py_modules=["folder_to_llm"],
    entry_points={
        'console_scripts': [
            'folder-to-llm=folder_to_llm:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
