#!/bin/bash

set -eu

module unload scitools
module load scitools

# set the library root path
CATNIP_ROOT_DIR="$(cd $(dirname $0) && pwd -P)"
CATNIP_LIB_DIR="${CATNIP_ROOT_DIR}/lib/catnip"
export LC_CTYPE=en_GB.utf8


FILES_TO_TEST=$(find . -type f -name '*.py')



function test_flake8 {
	echo -e "\033[1;32m[RUNNING FLAKE8 TESTS]\033[0m"
	flake8
}

function test_black {
	echo -e "\033[1;32m[RUNNING BLACK TESTS]\033[0m"
	module unload scitools
	module load scitools/experimental-current
        black $FILES_TO_TEST	

}

function test_documentation {
	echo -e "\033[1;32m[RUNNING DOCUMENTATION TESTS]\033[0m"
	echo "TODO"
}

function test_pytest {
	echo -e "\033[1;32m[RUNNING PY TESTS]\033[0m"
	cd $CATNIP_LIB_DIR	
	pytest -p no:warnings -v
}


# ----------------------------------
# tests starts here 
# ---------------------------------

# Run flake8 tests
test_flake8

# Run black codestyling tests
test_black


# Run black codestyling tests
test_documentation


# Run doc and unittests 
test_pytest


