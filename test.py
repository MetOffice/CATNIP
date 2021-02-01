import os



PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__))





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


req = pip_requirements("requirements")
print(req)
