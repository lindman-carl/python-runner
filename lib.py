from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.Eval import default_guarded_getiter


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


def execute_user_script(test_input: str, user_code: str):
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

    # Use regex to split the input string into a list of strings
    test_input_list = test_input.split(";")

    # Fix the indentation of the user code
    indented_user_code = adjust_indentation(user_code)

    # Wrap the user code in a function that can be called
    # printed is a magic variable that captures all printed output (PrintCollector)
    compile_code_string = f"""
def run_code():
    def input_generator(lines):
        for line in lines:
            yield str(line)
        while True:
            yield ""

    generator = input_generator({test_input_list})

    def input():
        return next(generator)
    
{indented_user_code}

    return printed

"""

    # Check for print statements in the user code
    # if not re.match(r".*print\(", compile_code_string, re.DOTALL):
    #     raise Exception("Print output expected")

    # Compile the user code that has been wrapped in a function and populated with the input
    try:
        compiled_code = compile_restricted(compile_code_string, "<inline>", mode="exec")
    except Exception as e:
        # If the user code fails to compile, return the error message
        return str(e)

    # Wrapper for the open function
    # open() is dangerous
    class OpenWrapper:
        def __init__(self, *args, **kw):
            if kw or len(args) > 1 or args[0] != 0:
                raise Exception("No file I/O allowed")

        def readlines(self):
            return test_input_list

        def read(self):
            return "\n".join(test_input_list)

        def readline(self):
            return test_input_list.pop(0)

        def __str__(self):
            return "<_io.TextIOWrapper name=0 mode='r' encoding='UTF-8'>"

    class PrintCollector:
        def __init__(self, _getattr_=None):
            self.txt = []
            self._getattr_ = _getattr_

        def write(self, text: str):
            self.txt.append(text.rstrip("\n"))

        def __call__(self):
            return "".join(self.txt)

        def _call_print(self, *objects, **kwargs):
            if kwargs.get("file", None) is None:
                kwargs["file"] = self
            else:
                self._getattr_(kwargs["file"], "write")

            print(*objects, **kwargs)

    # What globals are available to the user
    safe_globals = {
        "__imports__": [
            "math",
            "re",
            "itertools",
            "random",
            "datetime",
            "functools",
            "collections",
            "operator",
            "string",
            "json",
        ],
        "__builtins__": safe_builtins,
        "_getitem_": default_guarded_getitem,
        "_print_": PrintCollector,
        "_getiter_": default_guarded_getiter,
        "__name__": "restricted namespace",  # lol
        "__metaclass__": "restricted namespace",  # lol
        "next": next,
        "open": OpenWrapper,
    }

    # Create an empty locals dictionary, for capturing the printed output
    # all the printed output will be captured in the printed variable that is returned
    # from the run function, printed works like magic
    # all local functions that return something can be found in the locals dictionary
    locals = {}

    # Run this playaer
    exec(compiled_code, safe_globals, locals)

    # get the printed output from the run_code function
    output = locals["run_code"]()

    # Return the return value of the run_code function
    return output
