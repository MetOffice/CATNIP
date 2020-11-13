import os.path
import configparser


# The full path to the "catnip" package.
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

# The full path of test data directory
DATA_DIR = os.path.join(ROOT_PATH, "data")

# The full path of the KGO dir
KGO_DIR = os.path.join(ROOT_PATH, "kgo")
