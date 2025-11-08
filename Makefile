.PHONY: help install install-dev test lint format clean build publish docs

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)NEPSE Client - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install package dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements/base.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -r requirements/dev.txt
	pip install -e .
	pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v --cov=nepse_client --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Tests completed$(NC)"
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"

test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/ -v -m unit
	@echo "$(GREEN)✓ Unit tests completed$(NC)"

test-integration: ## Run only integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/ -v -m integration
	@echo "$(GREEN)✓ Integration tests completed$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	pytest-watch tests/ -v

lint: ## Run linters (flake8, mypy)
	@echo "$(BLUE)Running linters...$(NC)"
	uv run flake8 nepse_client tests --max-line-length=150 --extend-ignore=E203,W503
	uv run mypy nepse_client --ignore-missing-imports
	@echo "$(GREEN)✓ Linting completed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black nepse_client tests examples --line-length=100
	isort nepse_client tests examples --profile black --line-length=100
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code format...$(NC)"
	black nepse_client tests examples --check --line-length=100
	isort nepse_client tests examples --check --profile black --line-length=100

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "$(GREEN)✓ Cleaned$(NC)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	python -m build
	@echo "$(GREEN)✓ Build completed$(NC)"
	@ls -lh dist/

check-build: build ## Check distribution packages
	@echo "$(BLUE)Checking distribution packages...$(NC)"
	twine check dist/*
	@echo "$(GREEN)✓ Build check passed$(NC)"

publish-test: check-build ## Publish to TestPyPI
	@echo "$(YELLOW)Publishing to TestPyPI...$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Published to TestPyPI$(NC)"

publish: check-build ## Publish to PyPI
	@echo "$(RED)Publishing to PyPI...$(NC)"
	@read -p "Are you sure you want to publish to PyPI? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	twine upload dist/*
	@echo "$(GREEN)✓ Published to PyPI$(NC)"

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd docs && make html
	@echo "$(GREEN)✓ Documentation built$(NC)"
	@echo "$(YELLOW)Open: docs/_build/html/index.html$(NC)"

docs-serve: docs ## Build and serve documentation
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	cd docs/_build/html && python -m http.server 8000

coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	pytest tests/ --cov=nepse_client --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "$(YELLOW)Open: htmlcov/index.html$(NC)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	pip-audit
	bandit -r nepse_client/
	@echo "$(GREEN)✓ Security checks completed$(NC)"

version: ## Show current version
	@python -c "from nepse_client import __version__; print('Version:', __version__)"

bump-patch: ## Bump patch version (x.x.X)
	@echo "$(BLUE)Bumping patch version...$(NC)"
	bumpversion patch
	@echo "$(GREEN)✓ Version bumped$(NC)"

bump-minor: ## Bump minor version (x.X.0)
	@echo "$(BLUE)Bumping minor version...$(NC)"
	bumpversion minor
	@echo "$(GREEN)✓ Version bumped$(NC)"

bump-major: ## Bump major version (X.0.0)
	@echo "$(BLUE)Bumping major version...$(NC)"
	bumpversion major
	@echo "$(GREEN)✓ Version bumped$(NC)"

requirements: ## Generate requirements files
	@echo "$(BLUE)Updating requirements files...$(NC)"
	pip-compile requirements/base.in -o requirements/base.txt
	pip-compile requirements/dev.in -o requirements/dev.txt
	pip-compile requirements/test.in -o requirements/test.txt
	@echo "$(GREEN)✓ Requirements updated$(NC)"

verify: format lint test ## Run all verification steps
	@echo "$(GREEN)✓ All verifications passed!$(NC)"

release: verify build publish ## Full release process (verify, build, publish)
	@echo "$(GREEN)✓ Release completed!$(NC)"

init-project: ## Initialize new development environment
	@echo "$(BLUE)Initializing development environment...$(NC)"
	python -m venv venv
	@echo "$(YELLOW)Activate virtual environment:$(NC)"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\\Scripts\\activate  (Windows)"
	@echo ""
	@echo "$(YELLOW)Then run:$(NC) make install-dev"

example-sync: ## Run synchronous example
	@echo "$(BLUE)Running synchronous example...$(NC)"
	python examples/basic_usage.py

example-async: ## Run asynchronous example
	@echo "$(BLUE)Running asynchronous example...$(NC)"
	python examples/async_usage.py

shell: ## Start Python shell with package imported
	@echo "$(BLUE)Starting Python shell...$(NC)"
	python -c "from nepse_client import *; import code; code.interact(local=dict(globals(), **locals()))"

info: ## Show project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "==================="
	@python -c "from nepse_client import get_client_info; import json; print(json.dumps(get_client_info(), indent=2))"
	@echo ""
	@echo "$(BLUE)Python Version:$(NC) $$(python --version)"
	@echo "$(BLUE)Pip Version:$(NC) $$(pip --version | cut -d' ' -f2)"

tree: ## Show project structure
	@echo "$(BLUE)Project Structure$(NC)"
	@echo "==================="
	tree -I '__pycache__|*.pyc|*.egg-info|htmlcov|.git|venv|.pytest_cache|.mypy_cache' -L 3

git-status: ## Show git status with formatting
	@echo "$(BLUE)Git Status$(NC)"
	@echo "==========="
	@git status --short
	@echo ""
	@echo "$(BLUE)Recent Commits:$(NC)"
	@git log --oneline --graph --decorate -n 5

# Development workflow shortcuts
quick-test: format lint ## Quick format and lint check
	@echo "$(GREEN)✓ Quick checks passed$(NC)"

deploy-test: verify publish-test ## Verify and deploy to TestPyPI
	@echo "$(GREEN)✓ Deployed to TestPyPI$(NC)"

deploy-prod: verify publish ## Verify and deploy to PyPI
	@echo "$(GREEN)✓ Deployed to PyPI$(NC)"
