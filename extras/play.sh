#!/bin/bash
set -e
while IFS="" read -r p || [ -n "$p" ]
do
  printf '%s\n' "$p"
  echo $p | awk 'BEGIN {FS=" ,, ";}{print $2}' | xargs -r python cmd.py --play | xargs -r cvlc --play-and-exit 
done<$1
