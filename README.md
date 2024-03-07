# AFRY Open Python code runner

Python code runner for AFRY Open.

Python version: 3.12.2

## Running the code

**Dev environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# run the code with input strings, convenient
chmod +x dev_run.sh
./dev_run.sh

# run with command line arguments
# args: input_string: string(string[]), user_code: string
python3 runner.py "['1','2']" "print('hello world')"
```

**Docker**

```bash
docker build -t backend-python-runner .
docker run -p 5001:5001 backend-python-runner runner.py "['1','2']" "print('hello world')"
```

## Current limitations

- Does not work
