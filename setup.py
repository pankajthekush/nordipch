import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nordipch",
    version="0.0.4",
    author="Pankaj Kumar",
    author_email="pankajthekush@gmail.com",
    description="A Package to change NordVPN servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pankajthekush/nordipch",
    packages=['nordipch'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Windows 10",
    ],
    python_requires='>=3.6',
    install_requires=['requests>=2.22.0']
)