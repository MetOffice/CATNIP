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
				# Iterate through files to check whether they contain the expected
				# licence information. If any files do not contain the expected licence
				# information, then this test will fail.
read -d '' expected <<'__TEXT__' || true
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017-2020 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
__TEXT__


      echo $FILES_TO_TEST
			count=0
			for FILE in $FILES_TO_TEST; do
					# Check whether file has a size greater than zero.
					echo 'Checking: ' $FILE
					if [[ -s $FILE ]]; then
							file_contents=$(<$FILE)
							if [[ "$file_contents" != *"$expected"* ]]; then
								echo 'Licence information is not found in ' $FILE
								count=$((count+1))
							fi
					fi
			done
			if (( $count > 0 )); then
					return 1
			fi
}


function check_pytest {
	echo -e "\033[1;32mRunning pytest ...\033[0m"
	cd $CATNIP_LIB_DIR
	pytest -p no:warnings -v
}


# initializing the dict for summary
declare -A results


# test runs here ...

TESTS="flake8 black documentation license"
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
