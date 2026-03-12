# Justfile for openmotics development commands
# Install just: https://github.com/casey/just

# Default recipe - show available commands
default:
    @just --list

# Install/update all dependencies required to run the project
install:
    "./script/setup/bootstrap"

# Run all tests
test:
    "./script/test"

# Lint with ruff format + check
lint:
    "./script/lint"

# Run type-check, lint-cehck and spell-checkl
check:
    "./script/check"

# Clean build artifacts
clean:
    "./script/clean"

# Install pre-commit hooks
pre-commit-install:
    prek install

# Install pre-commit hooks
pre-commit-upgrade:
    prek autoupdate

# Run pre-commit hooks on all files
pre-commit-run:
    prek run --all-files

# Run all checks (lint, format, tests) before committing
pre-commit:
    just lint
    just test

# Show Python version
python-version:
    python --version
