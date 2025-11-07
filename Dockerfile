FROM public.ecr.aws/x8v8d7g8/mars-base:latest
WORKDIR /app

# System build dependencies for packages like lxml, h5py, etc.
# Assuming a Debian/Ubuntu base. If the base image uses a different distro,
# replace with the equivalent package manager commands.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       pkg-config \
       python3-dev \
       libxml2-dev \
       libxslt1-dev \
       zlib1g-dev \
       libffi-dev \
       libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Prefer a widely-available Python to maximize wheel availability
ENV UV_PYTHON=3.12

# Copy repository contents
COPY . .

# Install Python dependencies using uv (preinstalled in base image)
# Rely on an existing lockfile and perform a frozen sync.
# Install the optional 'distributed' extra deterministically from the lock.
RUN uv sync --frozen --extra distributed

# Start an interactive shell for development
CMD ["/bin/bash"]
