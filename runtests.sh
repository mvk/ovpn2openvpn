#!/bin/bash
[ -z "${VIRTUAL_ENV}" ] && . ./mkrunenv.sh ovpn 2.7 test
py.test -v .
