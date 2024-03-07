#!/bin/bash

# because pasting in the terminal sucks

test_input="['1','2']"

user_code=$(cat <<EOF
ants = int(input())
elephants = int(input())
if ants < elephants:
  print("LESS")
else:
  print("NO")
EOF)

python3 "runner.py" "$test_input" "$user_code"
