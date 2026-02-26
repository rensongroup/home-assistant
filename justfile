# Justfile for openmotics development commands
# Install just: https://github.com/casey/just

# Default recipe - show available commands
default:
    @just --list

# Install dependencies (pre-commit, ruff, etc.)
install:
    uv sync --all-extras --group dev

# Install only production dependencies
install-prod:
    uv sync

# Upgrade all dependencies to their latest versions
upgrade:
    uv lock --upgrade

# Run all tests
test:
    uvx pytest tests/

# Lint with ruff
lint:
    uvx ruff format --diff .

# Format code with ruff
format:
    uvx ruff format .

# Check formatting without making changes
format-check:
    uvx ruff format --check .

# Run lint and format check
check:
    just lint
    just format-check

# Build the package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf .eggs/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".coverage" -exec rm -f {} + 2>/dev/null || true

# Install pre-commit hooks
pre-commit-install:
    uvx prek install

# Install pre-commit hooks
pre-commit-upgrade:
    uvx prek autoupdate

# Run pre-commit hooks on all files
pre-commit-run:
    uvx prek run --all-files

# Run all checks (lint, format, tests) before committing
pre-commit:
    just lint
    just format-check
    just test

# Show Python version
python-version:
    uv run python --version
