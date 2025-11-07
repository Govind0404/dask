FROM public.ecr.aws/x8v8d7g8/mars-base:latest
WORKDIR /app

# Copy repository contents
COPY . .

# Install Python dependencies using uv (preinstalled in base image)
# Use frozen resolution to ensure reproducible installs
RUN uv sync --frozen

# Ensure test runner script is executable in container environments
RUN chmod +x test.sh || true

# Start an interactive shell for development
CMD ["/bin/bash"]
