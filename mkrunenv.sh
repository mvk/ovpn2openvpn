#!/bin/bash
vename="$1"
pyver="$2"
istest="$3"
reqs="requirements.txt"
reqs_test="requirements-test.txt"
vewrapper="virtualenvwrapper.sh"
veroot="${WORKON_HOME}/${vename}${pyver}"
which ${vewrapper} > /dev/null
[ $? -eq 0 ] || ( echo "FATAL: ${vewrapper} is not on path"; exit 1 )
source $( which ${vewrapper} )
[ -d "${veroot}" ] && ( echo "WARN: ${veroot} found, cleaning it up"; rm -fr "${veroot}" )
mkvirtualenv ${vename}${pyver} -p /usr/bin/python${pyver} -r ${reqs}
[ -n "${istest}" ] && pip install -r ${reqs_test}
