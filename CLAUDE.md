# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Shabunble is a security research project exploring techniques for creating Docker containers that discourage casual inspection of their contents. The project documents attempts to balance code obfuscation with practicality, acknowledging fundamental limitations in container security. The core approach uses multi-stage Docker builds where the deployment stage removes shell access and unnecessary tools. This repository is educational - it demonstrates both the techniques and their limitations through comparative examples.

## Build Commands

### Building Docker Images

Examples use either direct Docker commands or Docker Compose. Use direct Docker commands for simple examples, Docker Compose for multi-container setups:

```bash
# Build and run the basic unenterable example
cd unenterable_container
docker build -t unenterable_boomline .
docker run -t unenterable_boomline

# Build and run neural network examples
cd unenterable_neural_network/shellless
docker compose build
docker compose up

# Test injection attacks on unenterable containers
cd unenterable_container
docker run -it -v $PWD/../mount_injection:/injection unenterable_boomline /injection/python_shell.py

# Compare enterable vs unenterable versions
cd enterable_container && docker compose up  # Has shell access
cd unenterable_container && docker compose up  # No shell access
```

### Python Development

Requirements for neural network examples:
```bash
# Install in unenterable_neural_network directory
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project Structure

- `/unenterable_container` - Basic example: simple Python app with counter and ASCII art
- `/enterable_container` - Reference implementation with normal shell access
- `/unenterable_neural_network` - Advanced examples with PyTorch classifier
  - `/unobfuscated` - Standard single-stage build for comparison
  - `/shellless` - Multi-stage build using distroless Python image (no shell)
  - `/mazed` - Obfuscated paths and directory structure
  - `/influxdb2` - Database component for the classifier
- `/mount_injection` - Example tools for demonstrating container "break-in" techniques
- `/presentation` - Materials for presentations about the project
- `teaching_computers_to_lie.md` - Philosophical notes on obfuscation and computation

## Architecture Patterns

### Multi-Stage Build Pattern

All unenterable examples follow this pattern:
1. **Build stage**: Use full-featured image (python:3-slim) with shell, package managers, build tools
2. **Deployment stage**: Use minimal base (gcr.io/distroless/python3) that only contains Python runtime

### Virtual Environment Approach

For examples with dependencies (neural networks), the deployment stage:
- Creates venv in build stage with `python -m venv /opt/venv`
- Copies the entire venv to deployment stage: `COPY --from=build-env /opt/venv /opt/venv`
- Sets `PATH` and `PYTHONPATH` to use the venv Python and installed packages
- This works because distroless Python images lack pip and standard library packages

### Security Considerations

The repository documents that these techniques create "speed bumps" not security:
- Docker images can always be unpacked and inspected offline
- Entry points can be overridden with `docker run --entrypoint`
- Files can be mounted into containers at runtime
- The goal is to discourage casual inspection, not prevent determined analysis

### Testing and Comparison

The examples are designed to be tested against each other:
- Compare `/enterable_container` (full shell) vs `/unenterable_container` (distroless)
- Compare `/unobfuscated` (single-stage) vs `/shellless` (multi-stage) neural networks
- Use `/mount_injection` to test container breakout techniques
- The `mazed` example demonstrates path obfuscation effectiveness
- All examples can be unpacked and inspected to demonstrate container format transparency

## Dependencies

- Docker (all examples)
- Docker Compose (most examples)
- Python 3.11 (neural network examples)
- PyTorch, torchvision, influxdb-client, numpy (neural network requirements)

## Next Steps

The README mentions exploring confidential computing as a potential next direction for stronger security guarantees.