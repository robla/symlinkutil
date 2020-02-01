#!/bin/bash

summary="$0: provide the table of links to lnlookup.sh"
usageline="   usage: $0: [-q]"
usageline="     -q  quick version - returns if there's no cache"
usage="${summary}\n\n${usageline}\n\n"

fullhomedirflag=

while getopts q flags
do
  case $flags in
    q)   quickflag=1;;
    ?)   printf $usage
          exit 2;;
  esac
done

# shift off the flags using arithmetic expansion of OPTIND
shift $(($OPTIND - 1))

tmpfile=/tmp/lnlookup.tmp

if [ ! -d ${HOME} ]; then
  echo "HOME variable is weird: ${HOME}"
fi

# Note from robla 2020-01-31 - The calling script (lnlookup.sh) may be
# using "cacheme", thus making this extra logic superfluous.  It is
# nice having a temp file around, though, since I use the tempfile
# every now and then.

if [ ! -e ${tmpfile} ]; then
  if [ -z "$quickflag" ]; then
    find ${HOME} -type l | while read LINE; do printf "${LINE}\t$(readlink -f ${LINE})\n"; done > ${tmpfile}
    echo "lnlookup file created at ${tmpfile}" 1>&2
  else
    echo "no ${tmpfile} found.  oops" 1>&2
  fi
else
  echo "using cached ${tmpfile}" 1>&2
fi

cat "${tmpfile}"

