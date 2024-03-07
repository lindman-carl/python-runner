# Use an official Python runtime as a parent image
FROM python:3.12.2-bookworm

# Set the working directory in the container
WORKDIR /usr/src/python-runner

# Copy the current directory contents into the container at /usr/src/python-app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Port
EXPOSE 5001

# To run the application, no need to run the container without any user input
# CMD ["python3", "runner.py", "['1','2']", "userSubmittedCodeAsString"]
