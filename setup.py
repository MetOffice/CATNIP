import setuptools
from distutils.core import setup



with open("README.md", "r") as fh:
    long_description = fh.read()

def requirements():
    requirements = []
    fname = "requirements.txt"
    with open(fname, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            requirements.append(line)
    return requirements

setup(name='CATNIP',
      version='0.0.1',
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
      install_requires=requirements(),
      keywords = ["1", "2", "3"],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
     ]
)
