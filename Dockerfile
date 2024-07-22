FROM python:latest
LABEL authors="exkernel"

WORKDIR /blender-render-server

COPY . /blender-render-server

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    flatpak \
    libxi-dev \
    libxmu-dev \
    libxrender-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Add Flathub repository
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install Blender
RUN flatpak install -y flathub org.blender.Blender

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Listen on any host
CMD ["flask", "run", "--host=0.0.0.0"]
