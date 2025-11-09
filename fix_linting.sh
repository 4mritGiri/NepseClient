#!/bin/bash
# One-command fix for all linting issues
# Save this as fix_linting.sh and run: bash fix_linting.sh

set -e  # Exit on error

echo "========================================="
echo "Fixing Linting Issues"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run this from project root."
    exit 1
fi

# Install required tools
echo "📦 Installing/updating tools..."
uv pip install -q black isort autoflake flake8 flake8-docstrings flake8-bugbear

echo ""
echo "🔧 Step 1: Running Black (fixing line length)..."
uv run black --line-length=100 --target-version=py39 nepse_client tests examples docs/ 2>/dev/null || true

echo ""
echo "🔧 Step 2: Running isort (fixing import order)..."
uv run isort --profile=black --line-length=100 nepse_client tests examples

echo ""
echo "🔧 Step 3: Removing unused imports..."
uv run autoflake --in-place --remove-all-unused-imports --remove-unused-variables \
  --recursive nepse_client examples tests 2>/dev/null || true

echo ""
echo "========================================="
echo "✅ Automatic fixes complete!"
echo "========================================="
echo ""
echo "📝 Remaining manual fixes needed:"
echo ""
echo "1. Fix 5 B042 errors in nepse_client/exceptions.py:"
echo "   Lines: ~25, ~214, ~244, ~280, ~308"
echo ""
echo "   Pattern to fix:"
echo "   # Before:"
echo "   def __init__(self, message: str, code: str):"
echo "       self.code = code"
echo "       super().__init__(message)"
echo ""
echo "   # After:"
echo "   def __init__(self, message: str, code: str):"
echo "       super().__init__(message, code)  # Pass ALL args"
echo "       self.code = code"
echo ""
echo "========================================="
echo "🧪 Running checks..."
echo "========================================="
echo ""

# Run flake8 to see remaining issues
echo "Flake8 report:"
uv run flake8 nepse_client tests examples \
  --max-line-length=88 \
  --extend-ignore=E203,W503,E501,D212 \
  --per-file-ignores='*/__init__.py:F401' \
  --count --statistics 2>&1 || true

echo ""
echo "========================================="
echo "Next steps:"
echo "========================================="
echo "1. Manually fix the B042 errors (see above)"
echo "2. Run: pre-commit run --all-files"
echo "3. Run: git add -A && git commit -m 'fix: resolve linting issues'"
echo "4. Run: git push"
echo ""
