#!/bin/bash
# Run a benchmark script using all permutations of Python versions and commits.

set -e

benchmark="bm_create_proxy_cleaned.py"
declare -a py_versions=("3.11" "3.10" "3.9" "3.8")
declare -a commits=("83e8cd8f" "00bb7918" "f61f7395" "8ff8e264")

if [ $# -eq 0 ]
then
    echo "Usage: ./run.sh [BENCHMARK]"
    exit 1;
fi

for commit in ${commits[@]}
do
	git checkout ${commit} > /dev/null
	for py_version in ${py_versions[@]}
	do
		docker run \
			--rm \
			-it \
			-v $(pwd):/followthemoney \
			-e GIT_COMMIT=${commit} \
			python:${py_version} \
			bash -c "cd /followthemoney && pip3 install -e . &> /dev/null && python3 contrib/benchmarks/${benchmark}"
	done
done