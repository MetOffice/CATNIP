import setuptools
import os
from distutils.core import setup


PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

def pip_requirements(*args):
    requirements = []
    for name in args:
        fname = os.path.join(
            PACKAGE_DIR, "requirements", "{}.txt".format(name)
        )
        if not os.path.exists(fname):
            emsg = (
                f"Unable to find the {name!r} requirements file at {fname!r}."
            )
            raise RuntimeError(emsg)
        with open(fname, "r") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                requirements.append(line)
    return requirements


setup(name='mo-catnip',
      version='1.0.1',
      description='Climate analysis tool',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Met Office',
      author_email='catnip@metoffice.gov.uk',
      license = "BSD",
      url='https://github.com/MetOffice/CATNIP',
      packages=setuptools.find_packages(where='lib'),
      package_dir={"": "lib"},
      python_requires='>=3.6',
      install_requires=pip_requirements("requirements"),
      keywords = ["cmip", "climate", "analysis", "rcp", "iris"],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
     ]
)
