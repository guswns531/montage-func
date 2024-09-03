"""
MIT License

Copyright (c) 2024 Hyeon-Jun Jang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from parliament import Context
from flask import Request
from datetime import datetime
import subprocess
import os
import shutil
import socket
import json

# Get the hostname
hostname = socket.gethostname()

# Helper function to convert datetime objects to ISO format
def datetime_to_str(dt):
    return dt.isoformat() if dt else None

# Parse request body, json data or URL query parameters
def execute_function(req: Request) -> (str, int): # type: ignore
    if req.method == "POST":
        if req.is_json:
            # Capture the start time
            start_time = datetime.now()

            # Save the JSON data to a Python dictionary
            data = req.get_json()

            job_id = list(data.keys())[0]
            job_data = data[job_id]
            
            # Extract and print command, arguments, inputs, and outputs
            run_id = job_data.get('runid')
            run_dir = job_data.get('rundir')
            command = job_data.get('command')
            arguments = job_data.get('arguments')
            inputs = job_data.get('inputs')
            outputs = job_data.get('outputs')

            # Prepare the full command with arguments
            full_command = [command] + arguments
                        
            # Create a directory for the job_id (runid)
            runid_directory = os.path.join(os.getcwd(), run_id)
            os.makedirs(runid_directory, exist_ok=True)

            # Save the current working directory to return back after execution
            original_directory = os.getcwd()
            
            ret_status = 200
            output = ""  # Default value
            error = ""   # Default value

            try:
                # Capture the inputIO time
                inputIO_time = datetime.now()

                # Copy inputs from rundir to runid_directory
                for input_file in inputs:
                    shutil.copy(os.path.join(run_dir, input_file), runid_directory)

                # Change the working directory to the new runid directory
                os.chdir(runid_directory)

                # Set up environment variables (copy the existing environment and update it)
                env = os.environ.copy()
                env["PATH"] = f"/workspace/bin:{env['PATH']}"

                # Capture the command time
                command_time = datetime.now()

                # Execute the command
                result = subprocess.run(full_command, check=True, capture_output=True, text=True, env=env)
                # output = result.stdout
                # error = result.stderr

                # Capture the outputIO time
                outputIO_time = datetime.now()

                # Copy outputs from runid_directory to rundir
                for output_file in outputs:
                    shutil.copy(os.path.join(runid_directory, output_file), run_dir)
                
            except subprocess.CalledProcessError as e:
                output = e.output
                error = e.stderr
                outputIO_time = datetime.now()
                ret_status = 500
            finally:
                # Return to the original working directory
                os.chdir(original_directory)

                # Delete the runid directory and its contents
                shutil.rmtree(runid_directory)

            # Capture the end time
            end_time = datetime.now()
            
            # Create a JSON structure with all the information
            result_json = {
                "ID": job_id,
                "runID": run_id,
                "Command": command,
                "Arguments": arguments,
                "Inputs": inputs,
                "Outputs": outputs,
                "Start Time": datetime_to_str(start_time),
                "InputIO Time": datetime_to_str(inputIO_time),
                "Command Time": datetime_to_str(command_time),
                "OutputIO Time": datetime_to_str(outputIO_time),
                "End Time": datetime_to_str(end_time),
                "Hostname": hostname,
                "Execution Output": output,
                "Execution Error": error
            }
                
            return json.dumps(result_json, indent=2) + "\n", ret_status

        else:
            # MultiDict needs some iteration
            ret = "{"

            for key in req.form.keys():
                ret += '"' + key + '": "'+ req.form[key] + '", '

            return ret[:-2] + "}\n" if len(ret) > 2 else "{}", 200

    elif req.method == "GET":
        # MultiDict needs some iteration
        ret = "{"

        for key in req.args.keys():
            ret += '"' + key + '": "' + req.args[key] + '", '

        return ret[:-2] + "}\n" if len(ret) > 2 else "{}", 200

def main(context: Context):
    """
    Function template
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """

    # Add your business logic here
    print("Received request")

    if 'request' in context.keys():
        return execute_function(context.request)
    else:
        print("Empty request", flush=True)
        return "{}", 200