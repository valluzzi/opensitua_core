import os,re
import setuptools

PACKAGE_NAME = "opensitua_core"

def get_version():
    VERSIONFILE = os.path.join(PACKAGE_NAME, '__init__.py')
    initfile_lines = open(VERSIONFILE, 'rt').readlines()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(VSRE, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError('Unable to find version string in %s.' % (VERSIONFILE,))

setuptools.setup(
    name=PACKAGE_NAME,
    version=version,
    author="Valerio Luzzi",
    author_email="valluzzi@gmail.com",
    description="core functions package",
    long_description="core functions package",
    url="https://github.com/valluzzi/%s.git"%(PACKAGE_NAME),
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['jinja2',
                      'six', 'argparse', 'xmljson',
                      'openpyxl',
                      'xlrd', 'xlwt', 'xlutils', 'numpy',
                      'rarfile']
)
