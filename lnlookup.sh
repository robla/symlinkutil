#!/bin/bash

summary="$0: find symlinks in HOMEDIR to a given path"
usageline="   usage: $0: [-f] path"
usageline="     -f  full home dir rather than tilde"
usage="${summary}\n\n${usageline}\n\n"

fullhomedirflag=

while getopts f name
do
  case $name in
    f)   fullhomedirflag=1;;
    ?)   printf $usage
          exit 2;;
  esac
done

# shift off the flags using arithmetic expansion of OPTIND
shift $(($OPTIND - 1))

lookuptable=lnlookup-table.sh
ltcommand="cacheme $(dirname $(readlink -f ${BASH_SOURCE[0]}))/${lookuptable}"

if [ ! -d ${HOME} ]; then
  echo "HOME variable is weird: ${HOME}"
fi

if [ ! -z "$fullhomedirflag" ]; then
  trimcmd="myxtrim"
else
  trimcmd="myxtrim -t"
fi

if [ -e "$1" ]; then
  echo "$(${trimcmd} $(dirname .myxroot))/$1 links to $(${trimcmd} $1)"
  echo "Symlinks to $(${trimcmd} $1):"
  grep "$(readlink -f $1)$" <($ltcommand) |
    while IFS=$'\t' read -a lnArray; do
      printf "$(${trimcmd} $(dirname ${lnArray[0]}))/$(basename ${lnArray[0]})\n"
    done
else
  echo "please provide a target to look up"
fi
