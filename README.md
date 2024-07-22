# Blender Render Server

## Overview

This simple Flask-powered server allows you to offload Blender rendering tasks to a server with Blender installed. It's particularly useful if you don’t have access to a machine with a high-performance GPU.

## Features

- **Upload Blender Files**: Easily upload `.blend` files to the server.
- **Render with Blender**: The server processes the render using Blender and your specified settings.
- **Download Results**: Get the rendered output files directly from the server.

## How It Works

1. **Upload**: Send your `.blend` file to the server through the web interface.
2. **Render**: The server uses Blender to process your file and generate the output.
3. **Download**: Once rendering is complete, download the result from the server.

## Requirements

- **Blender**: Ensure Blender is installed on the server.
- **Flask**: The server uses Flask to handle web requests.

## Setup

### On bare metal
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ExtKernel/blender-render-server
   ```
2. Navigate to the Project Directory:
   ```bash
   cd blender-render-server
   ```
3. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Server:
   ```bash
   flask run
   ```
   
### In a Docker container
The Docker image of this application contains both the server and Blender, so it works "out of the box".

1. **Pull the Docker image from Docker hub**
   Download the latest Docker image from Docker Hub:
   ~~~bash
   docker pull exkernel/blender-render-server:latest
   ~~~

2. **Run a container using the image**
   Start a container from the downloaded image:
   ~~~bash
   docker run -d -p 5000:5000 exkernel/blender-render-server:latest
   ~~~
   You can specify any desirable port, the application is listening on any host.
3. **Access the web UI**
   Open your web browser and go to the following URL to access the web UI:
   ~~~bash
   http://<host>:<port>/
   ~~~
   Replace <host> with your Docker host's IP address or domain name, and <port> with the port you specified or the default port (5000).

## Troubleshooting
- File Type Not Allowed: Ensure you're uploading a ```.blend``` file.
- Render Process Failed: Check Blender installation and server logs for errors.

## Notes
- For production use, disable debug mode and ensure your server is properly secured.

## License
This project is licensed under the GPL-3.0 License. See the LICENSE file for details.
