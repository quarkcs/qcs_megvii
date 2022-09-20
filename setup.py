from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in megvii_integration/__init__.py
from megvii_integration import __version__ as version

setup(
	name="megvii_integration",
	version=version,
	description="Integration for Megvii",
	author="QCS",
	author_email="info@quarkcs.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
