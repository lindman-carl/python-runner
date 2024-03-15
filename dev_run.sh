#!/bin/bash

# because pasting in the terminal sucks

test_input="1,2"

user_code=$(cat <<EOF
ants = int(input())
elephants = int(input())
if ants < elephants:
  print("LESS")
else:
  print("NO")
EOF)

user_code2=$(cat <<EOF
print(open(0).read())
EOF)

python3 "runner.py" "$test_input" "$user_code2"
