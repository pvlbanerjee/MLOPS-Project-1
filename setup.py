from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="my_package", # Replace with your package name
    version="0.1.0",  # Replace with your package version
    author="Pavel Baanerjee",
    packages=find_packages(),
    install_requires=requirements,
)               