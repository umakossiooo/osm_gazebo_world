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
        jq && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    python --version && java -version

# Python dependencies
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      colorama \
      shapely \
      osmium

# OSM2World setup - expects jar to be copied during build
RUN mkdir -p /opt/osm2world

ENV OSM2WORLD_JAR=/opt/osm2world/OSM2World.jar

WORKDIR /app

# Create maps directory for volume mount
RUN mkdir -p /maps

# Copy converter script, OSM2World jar and dependencies
COPY convert_osm_to_gazebo.py /app/convert_osm_to_gazebo.py
COPY OSM2World.jar /opt/osm2world/OSM2World.jar
COPY lib/ /opt/osm2world/lib/

# Default command shows help
CMD ["python", "/app/convert_osm_to_gazebo.py", "--help"]


