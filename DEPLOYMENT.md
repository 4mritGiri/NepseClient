# Deployment Guide for nepse-client

This guide covers how to build, test, and publish the nepse-client package to PyPI.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Git** for version control
3. **PyPI account** (https://pypi.org/account/register/)
4. **TestPyPI account** (https://test.pypi.org/account/register/) for testing

## 🛠️ Setup

### 1. Install Build Tools

```bash
pip install --upgrade pip setuptools wheel build twine
```

### 2. Configure PyPI Credentials

Create/edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-api-token-here
```

**Security Note**: Use API tokens instead of passwords. Generate tokens at:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

## 🔍 Pre-Deployment Checklist

### 1. Update Version Number

Update version in:
- `setup.py`
- `pyproject.toml`
- `nepse_client/__init__.py`
- `CHANGELOG.md`

```python
# nepse_client/__init__.py
__version__ = "1.0.0"
```

### 2. Update Documentation

- [ ] Update README.md with new features
- [ ] Update CHANGELOG.md with changes
- [ ] Ensure all docstrings are complete
- [ ] Update examples if needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nepse_client --cov-report=html

# Ensure coverage is above 80%
coverage report
```

### 4. Run Code Quality Checks

```bash
# Format code
black .
isort .

# Lint code
flake8 nepse_client tests

# Type check
mypy nepse_client

# Run pre-commit hooks
pre-commit run --all-files
```

### 5. Test Installation Locally

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build

# Install locally
pip install dist/nepse_client-1.0.0-py3-none-any.whl

# Test import
python -c "from nepse_client import Nepse, AsyncNepse; print('Success!')"

# Uninstall
pip uninstall nepse-client
```

## 🧪 Testing on TestPyPI

### 1. Upload to TestPyPI

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

### 2. Test Installation from TestPyPI

```bash
# Create fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nepse-client

# Test the package
python -c "from nepse_client import Nepse; client = Nepse(); print('TestPyPI installation successful!')"

# Deactivate and remove test environment
deactivate
rm -rf test-env
```

## 🚀 Publishing to PyPI

### 1. Final Checks

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] TestPyPI installation successful
- [ ] Git repository clean
- [ ] CHANGELOG.md updated

### 2. Tag Release

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. Upload to PyPI

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build distribution
python -m build

# Verify build
twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### 4. Verify PyPI Installation

```bash
# Create fresh environment
python -m venv verify-env
source verify-env/bin/activate  # On Windows: verify-env\Scripts\activate

# Install from PyPI
pip install nepse-client

# Test
python -c "from nepse_client import Nepse; print('PyPI installation successful!')"

# Cleanup
deactivate
rm -rf verify-env
```

## 📝 Post-Deployment Tasks

### 1. Create GitHub Release

1. Go to https://github.com/yourusername/nepse-client/releases
2. Click "Draft a new release"
3. Select the tag you created
4. Add release notes from CHANGELOG.md
5. Attach distribution files (optional)
6. Publish release

### 2. Update Documentation

If using Read the Docs:
- Trigger documentation build
- Verify docs are updated

### 3. Announce Release

- Update README badges if needed
- Post on relevant forums/communities
- Update social media

## 🔄 Continuous Integration/Deployment

### GitHub Actions Example

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## 🛡️ Security Best Practices

1. **Never commit credentials** - Use environment variables or secrets
2. **Use API tokens** instead of passwords
3. **Enable 2FA** on PyPI account
4. **Scan dependencies** for vulnerabilities
5. **Sign releases** with GPG keys (optional)

```bash
# Sign releases
gpg --detach-sign -a dist/nepse_client-1.0.0.tar.gz

# Upload with signature
twine upload dist/* dist/*.asc
```

## 🐛 Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/
python -m build
```

### Upload Fails - "File already exists"

```bash
# Version already published - bump version number
# Edit version in setup.py, pyproject.toml, and __init__.py
```

### Import Errors After Installation

```bash
# Check package structure
tar -tzf dist/nepse_client-1.0.0.tar.gz

# Verify MANIFEST.in includes all necessary files
```

### Missing Dependencies

```bash
# Ensure all dependencies in setup.py and pyproject.toml match
# Test in fresh virtual environment
```

## 📞 Support

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/yourusername/nepse-client/issues)
2. Review PyPI packaging documentation
3. Ask on Python packaging forums

## 📚 Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)