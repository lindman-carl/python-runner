import sys
import os
from lib import execute_user_script

if __name__ == "__main__":
    # args:
    # 1. test_input: The input to pass to the user code. Comma separated strings "'1','2'"
    # 2. user_code: The user code to execute. Can be a text string or a file path.

    test_input = sys.argv[1]
    user_code = sys.argv[2]

    # handle user code if it's a file path
    if os.path.isfile(user_code):
        with open(user_code, "r") as f:
            user_code = f.read()

    # Run the user code
    output = execute_user_script(test_input, user_code)

    # Output the result
    print(output)
