FROM ubuntu:22.04

# Install Python 3.10, Java (for OSM2World), and system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        openjdk-17-jre-headless \
        ca-certificates \
        curl \
        unzip \
        git \
        jq \
        python3-numpy \
        gdal-bin \
        python3-gdal \
        # X11 libraries for Java headless mode
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxtst6 \
        libxi6 \
        xvfb && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    python --version && java -version

# Configure Java for headless mode by default
ENV JAVA_TOOL_OPTIONS="-Djava.awt.headless=true"

# Python dependencies
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      colorama \
      shapely \
      osmium \
      numpy

# OSM2World setup - expects jar to be copied during build
RUN mkdir -p /opt/osm2world

ENV OSM2WORLD_JAR=/opt/osm2world/OSM2World.jar

WORKDIR /app

# Create maps directory for volume mount
RUN mkdir -p /maps

# Copy converter scripts, OSM2World jar and dependencies
COPY convert_osm_to_gazebo.py /app/convert_osm_to_gazebo.py
COPY clean_osm_data.py /app/clean_osm_data.py
COPY osm_to_gazebo.py /app/osm_to_gazebo.py
COPY fix_mesh_normals.py /app/fix_mesh_normals.py
COPY fix_orientation.py /app/fix_orientation.py
COPY optimize_world.py /app/optimize_world.py
COPY optimize_complete.py /app/optimize_complete.py
COPY utils.py /app/utils.py
COPY OSM2World.jar /opt/osm2world/OSM2World.jar
COPY lib/ /opt/osm2world/lib/

# Make scripts executable
RUN chmod +x /app/*.py

# Create OSM2World headless wrapper
RUN echo '#!/bin/bash' > /usr/local/bin/osm2world-headless && \
    echo 'export _JAVA_OPTIONS="-Djava.awt.headless=true -Xmx2g"' >> /usr/local/bin/osm2world-headless && \
    echo 'java -Djava.awt.headless=true -Xmx2g "$@"' >> /usr/local/bin/osm2world-headless && \
    chmod +x /usr/local/bin/osm2world-headless

# Create Xvfb wrapper script
RUN echo '#!/bin/bash' > /usr/local/bin/xvfb-run-osm2world && \
    echo 'xvfb-run --server-args="-screen 0 1280x1024x24" java "$@"' >> /usr/local/bin/xvfb-run-osm2world && \
    chmod +x /usr/local/bin/xvfb-run-osm2world

# Default command shows help
CMD ["python", "/app/osm_to_gazebo.py", "--help"]

