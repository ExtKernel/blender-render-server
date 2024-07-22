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

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ExtKernel/blender-render-server
   ```
2. Navigate to the Project Directory:
   ```bash
   cd blender-render-server
   ```
4. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the Server:
   ```bash
   python app.py
   ```

## Troubleshooting
- File Type Not Allowed: Ensure you're uploading a .blend file.
- Render Process Failed: Check Blender installation and server logs for errors.

## Notes
- For production use, disable debug mode and ensure your server is properly secured.

## License
This project is licensed under the GPL-3.0 License. See the LICENSE file for details.
