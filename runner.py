import sys
import os

from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.PrintCollector import PrintCollector


def adjust_indentation(user_code, indent_len=4):
    """
    Adjusts the indentation of the given code.

    :param user_code: The code to adjust.
    :param indent_len: The number of spaces to indent each line.
    :return: The adjusted code.
    """
    indent = " " * indent_len
    indented_user_code = []

    # Calculate the number of spaces the user code is indented by
    # Also check that the indentation is consistent
    detected_indentation = -1

    for line in user_code.split("\n"):
        if line.startswith(" "):
            detected_indentation = len(line) - len(line.lstrip())
            break

    # Adjust the indentation of each line to match my indentation
    for line in user_code.split("\n"):
        if not line.lstrip():
            indented_user_code.append(indent + line)
            continue

        line_indentation_level = len(line) - len(line.lstrip())
        indented_line = (
            indent
            + indent * (line_indentation_level // detected_indentation)
            + line.lstrip()
        )

        indented_user_code.append(indented_line)

    return "\n".join(indented_user_code)


def execute_user_script(test_input, user_code):
    """
    Executes user-submitted Python script securely using RestrictedPython.
    This restricts the user code to a safe subset of Python, preventing it from
    accessing anything it shouldn't.

    !! Does not handle memory or cpu usage !!
    This is limited by the docker container that runs the python code.

    :param test_input: String containing the input to pass to the user code.
    :param user_code: String containing the Python code to execute.
    :return: String array containing the printed output of the user code.
    """

    # Fix the indentation of the user code
    indented_user_code = adjust_indentation(user_code)

    code_with_input = f"""
def run_code():

    def input_generator(lines):
        for line in lines:
            yield line
        while True:
            yield ""

    generator = input_generator({test_input.split(",")})

    def input():
        return next(generator)

{indented_user_code}

    return printed
"""

    # Replace the input() function with a custom get_input() function
    final_user_code = code_with_input
    # .replace(
    #     "input()", "input_handler.get_input()", -1
    # )

    print("Final user code:\n" + final_user_code + "\n")

    # Compile the user code that has been wrapped in a function and populated with the input
    byte_code = compile_restricted(final_user_code, "<inline>", mode="exec")

    # What globals are available to the user
    safe_globals = {
        "__builtins__": safe_builtins,
        "_getitem_": default_guarded_getitem,
        "_print_": PrintCollector,
        "__name__": "restricted namespace",  # lol
        "__metaclass__": "restricted namespace",  # lol
        "next": "restricted namespace",  # lol
    }

    # Create an empty locals dictionary, for capturing the printed output
    # all the printed output will be captured in the printed variable that is returned
    # from the run function, printed works like magic
    # all local functions that return something can be found in the locals dictionary
    locals = {}

    # Run this playaer
    exec(byte_code, safe_globals, locals)

    print("Locals:\n" + str(locals) + "\n")
    print("run_code:\n" + str(locals["run_code"]) + "\n")
    # print type of run_code
    print("Type of run_code:\n" + str(type(locals["run_code"])) + "\n")

    output = locals["run_code"]()

    # Return the return value of the run_code function
    return output


if __name__ == "__main__":
    # args:
    # 1. test_input: The input to pass to the user code. Comma separated string.
    # 2. user_code: The user code to execute. Can be a text string or a file path.

    test_input = sys.argv[1]

    user_code = sys.argv[2]

    # handle file as user code
    if os.path.isfile(user_code):
        with open(user_code, "r") as f:
            user_code = f.read()

    print("Test input:\n" + test_input + "\n")
    print("User code:\n" + user_code + "\n")

    # Execute the user script
    output = execute_user_script(test_input, user_code)

    # Output the result
    print("Output:\n" + output)


#
## input input variants
#

# 1. input_generator

#     code_with_input = f"""
# def run_code():

#     def input_generator(lines):
#         for line in lines:
#             yield line
#         while True:
#             yield ""

#     generator = input_generator({test_input.split(",")})

#     def input():
#         return next(generator)

# {indented_user_code}

#     return printed
# """

# 2. InputHandler class

#     code_with_input = f"""
# class InputHandler:
#     def __init__(self, lines):
#         self.lines = lines
#         self.index = 0

#     def get_input(self):
#         if self.index < len(self.lines):
#             line = self.lines[self.index]
#             self.index = self.index + 1
#             return line
#         else:
#             return ""


# def run_code():

#     input_handler = InputHandler({test_input.split(",")})

# {indented_user_code}

#     return printed
#     """.strip()
