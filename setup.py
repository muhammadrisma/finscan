from setuptools import setup, find_packages

setup(
    name="finscan",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain",
        "langchain-community",
    ],
    python_requires=">=3.8",
) 