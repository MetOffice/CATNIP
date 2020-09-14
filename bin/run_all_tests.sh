#!/bin/bash


module load scitools

# set the library root path
CATNIP_ROOT_DIR="$(cd $(dirname $0)/../ && pwd -P)"


CATNIP_LIB_DIR="${CATNIP_ROOT_DIR}/lib/catnip"
export LC_CTYPE=en_GB.utf8


FILES_TO_TEST=$(find $CATNIP_LIB_DIR -type f -name '*.py')


function check_flake8 {
	echo -e "\033[1;32mRunning flake8 tests ...\033[0m"
	flake8
}

function check_black {
	echo -e "\033[1;32mRunning black tests ...\033[0m"
	module unload scitools
	module load scitools/experimental-current
        black $FILES_TO_TEST

}

function check_documentation {
	echo -e "\033[1;32mChecking documentation ...\033[0m"
	# Build documentation as test.
	cd $CATNIP_ROOT_DIR/docsrc
	make github
}

function check_license {
        echo -e "\033[1;32mChecking for license ...\033[0m"
        echo "TODO"
}

function check_pytest {
	echo -e "\033[1;32mRunning pytest ...\033[0m"
	cd $CATNIP_LIB_DIR
	pytest -p no:warnings -v
}


# initializing the dict for summary
declare -A results


# test runs here ...

TESTS="flake8 black documentation license pytest"
for TEST_NAME in $TESTS; do
    "check_$TEST_NAME"
    ret=$?
		if [ $ret = "0" ]; then
			results["$TEST_NAME"]="\033[1;32m[PASS]\033[0m"
		else
			results["$TEST_NAME"]="\033[1;31m[FAIL]\033[0m"
		fi

done

# printing the summary
echo -e "\n\033[1;34m[TEST SUIT COMPLETE]\033[0m"
for key in ${!results[@]}; do
    echo -e ${key} ' check ' ${results[${key}]}
done
