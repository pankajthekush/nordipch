import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

current_path = os.path.dirname(os.path.realpath(__file__))
print(current_path)
from glob import glob
setuptools.setup(
    name="nordipch",
    version="0.3",
    author="Pankaj Kumar",
    author_email="pankajthekush@gmail.com",
    entry_points ={'console_scripts': ['nchange = nordipch.nordipch:check_file_connect']},
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
    install_requires=['requests>=2.22.0'],
    data_files = [(os.path.join(current_path, 'jslit/about'), glob('nordipch/*.json'))]
)