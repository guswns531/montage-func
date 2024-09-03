## Montage knative Function Deployment

### Project Overview
This project provides a guide for deploying the **Montage Function** on a Knative-based environment. 

It utilizes `PersistentVolume` and `PersistentVolumeClaim` to manage data storage, and the function is executed in a Python runtime environment. 

The function implementation is based on a Python HTTP Function template, which provides a simple and efficient way to handle HTTP requests within a serverless architecture.

### Prerequisites

- Docker: You’ll need Docker installed to build the Docker image required for the function.
- Kubernetes with Knative: A Kubernetes environment with Knative installed is required to deploy and run the service.
- Knative function: Download and set up the Knative function CLI:
  ```bash
  wget https://github.com/knative/func/releases/download/knative-v1.15.0/func_linux_amd64
  mv func_linux_amd64 func
  chmod +x func
  mv func /home/$USER/go/bin
  func version
  ```

### File Descriptions

1. **func.py**:  
   This Python file contains the core function logic that will be deployed as a Knative service.
   - **Description**: The script processes incoming HTTP requests and executes the corresponding command using the `montage` binary located in the `bin` directory. Based on the request payload, it constructs and runs the command to utilize the `montage` functionality. The implementation is based on a Python HTTP Function template, making it well-suited for handling HTTP-based interactions in a serverless environment.

   **Example Execution**:
   ```bash
   curl -X POST http://montage-func.default.127.0.0.1.sslip.io -H "Content-Type: application/json" -d '{
     "ID0000001": {
       "name": "mProject",
       "runid": "run00001",
       "rundir": "/mnt/data/montage-data/2MASS-J-D1",
       "command": "mProject",
       "arguments": ["-X", "2mass-atlas-980914s-j0700056.fits", "p2mass-atlas-980914s-j0700056.fits", "region-oversized.hdr"],
       "inputs": ["2mass-atlas-980914s-j0700056.fits", "region-oversized.hdr"],
       "outputs": ["p2mass-atlas-980914s-j0700056.fits", "p2mass-atlas-980914s-j0700056_area.fits"]
     }
   }'
   ```

   **Sample Output**:
   ```json
   {
     "ID": "ID0000001",
     "runID": "run00001",
     "Command": "mProject",
     "Arguments": [
       "-X",
       "2mass-atlas-980914s-j0700056.fits",
       "p2mass-atlas-980914s-j0700056.fits",
       "region-oversized.hdr"
     ],
     "Inputs": [
       "2mass-atlas-980914s-j0700056.fits",
       "region-oversized.hdr"
     ],
     "Outputs": [
       "p2mass-atlas-980914s-j0700056.fits",
       "p2mass-atlas-980914s-j0700056_area.fits"
     ],
     "Start Time": "2024-09-03T17:00:26.022749",
     "InputIO Time": "2024-09-03T17:00:26.022853",
     "Command Time": "2024-09-03T17:00:26.024116",
     "OutputIO Time": "2024-09-03T17:00:38.095332",
     "End Time": "2024-09-03T17:00:38.103178",
     "Hostname": "montage-func-00001-deployment-7bd7b66ff7-v4lts",
     "Execution Output": "",
     "Execution Error": ""
   }
   ```

2. **Dockerfile**:  
   This file is used to build a Python-based Docker image.
   - **Purpose**: The Dockerfile copies the `montage` binary from the `bin` folder and the necessary libraries from the `lib` folder into the Docker image. These components are crucial for the function’s operation.
   - **COPY Instructions**: The `bin` and `lib` folders are copied into the Docker container during the build process, ensuring the `montage` binary and its dependencies are available for use by the function.

3. **build.sh**:  
   A script file for building the project. This script first builds the Knative function using the Knative Function CLI, and then it proceeds to copy the required libraries from the `lib` directory into the Docker image through the `Dockerfile`.
   - **Usage**: Run this script to perform the initial build using the Knative function CLI, followed by the Docker build and push to the registry.

   ```bash
   sh ./build.sh
   ```

4. **montage-volume.yaml**:  
   Defines the `PersistentVolume(PV)` and `PersistentVolumeClaim(PVC)` resources.
   - **PersistentVolume**: Allocates 1Gi of storage and mounts it to the path `/mnt/data`.
   - **PersistentVolumeClaim**: Requests 1Gi of storage with the `ReadWriteOnce` access mode.

5. **montage-func.yaml**:  
   Defines the Knative-based `Service` resource.
   - **metadata**: Creates a Knative service named `montage-func`, which runs in a Python runtime environment.
   - **spec**:
     - **containers**: Deploys a container using the `guswns531/montage-func:v2` image and mounts the PVC to the path `/mnt/data`.

### Deployment Steps

1. **Build Docker Image**:
   - Execute the build script to create the Docker image and push it to the Docker registry:
   ```bash
   sh ./build.sh
   ```

2. **Configure PersistentVolume and PersistentVolumeClaim**:
   - Apply the `montage-volume.yaml` to set up the PV and PVC:
   ```bash
   kubectl apply -f montage-volume.yaml
   ```

3. **Deploy Knative Service**:
   - Apply the `montage-func.yaml` to deploy the service on Knative:
   ```bash
   kubectl apply -f montage-func.yaml
   ```

4. **Verify Service Deployment**:
   - Check the status of the deployed Knative service:
   ```bash
   kubectl get services.serving.knative.dev -n default
   ```

### Notes
- This project is designed to run on a Knative and Kubernetes environment.
- Data persistence is ensured through the configuration of `PersistentVolume` and `PersistentVolumeClaim`.
- The service is implemented as a serverless function running in a Python environment, with capabilities for automatic scaling.
- The `montage` binary, located in the `bin` directory, along with the necessary libraries from the `lib` directory, are integral to the function’s operation. The `func.py` script utilizes these resources to execute commands based on incoming requests.
- The function implementation is based on a Python HTTP Function template, providing a streamlined method for handling HTTP requests in a serverless architecture.