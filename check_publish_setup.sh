#!/bin/bash
# Test script to verify publish workflow setup
# Run: bash check_publish_setup.sh

set -e

echo "========================================="
echo "Testing Publish Workflow Setup"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in a git repo
if [ ! -d ".git" ]; then
   echo -e "${RED}❌ Not in a git repository${NC}"
   exit 1
fi

echo "📋 Checklist:"
echo ""

# 1. Check workflow file exists
echo -n "1. Workflow file exists... "
if [ -f ".github/workflows/publish.yml" ]; then
   echo -e "${GREEN}✓${NC}"
else
   echo -e "${RED}✗${NC}"
   echo "   Create .github/workflows/publish.yml"
   exit 1
fi

# 2. Check pyproject.toml exists
echo -n "2. pyproject.toml exists... "
if [ -f "pyproject.toml" ]; then
   echo -e "${GREEN}✓${NC}"
else
   echo -e "${RED}✗${NC}"
   exit 1
fi

# 3. Check package name in pyproject.toml
echo -n "3. Package name configured... "
PACKAGE_NAME=$(grep -m 1 '^name = ' pyproject.toml | cut -d'"' -f2)
if [ -n "$PACKAGE_NAME" ]; then
   echo -e "${GREEN}✓${NC} ($PACKAGE_NAME)"
else
   echo -e "${RED}✗${NC}"
   exit 1
fi

# 4. Check version in pyproject.toml
echo -n "4. Version configured... "
VERSION=$(grep -m 1 '^version = ' pyproject.toml | cut -d'"' -f2)
if [ -n "$VERSION" ]; then
   echo -e "${GREEN}✓${NC} (v$VERSION)"
else
   echo -e "${RED}✗${NC}"
   exit 1
fi

# 5. Check if package can be built
# 5. Check if package can be built with uv
echo -n "5. Package can be built with uv... "
if uv build --help &> /dev/null; then
   echo -e "${GREEN}✓${NC}"
else
   echo -e "${YELLOW}⚠${NC} (uv build command not available)"
   echo "   Ensure uv is installed: pip install uv (or how you installed it)"
fi

# 6. Check tests exist
echo -n "6. Tests directory exists... "
if [ -d "tests" ]; then
   echo -e "${GREEN}✓${NC}"
else
   echo -e "${YELLOW}⚠${NC} (no tests/ directory)"
fi

# 7. Check GitHub CLI (optional)
echo -n "7. GitHub CLI installed... "
if command -v gh &> /dev/null; then
   echo -e "${GREEN}✓${NC}"

   # Check if authenticated
   if gh auth status &> /dev/null; then
      echo -e "   ${GREEN}✓${NC} Authenticated"
   else
      echo -e "   ${YELLOW}⚠${NC} Not authenticated (run: gh auth login)"
   fi
else
   echo -e "${YELLOW}⚠${NC} (optional - install for easier workflow management)"
fi

echo ""
echo "========================================="
echo "PyPI Configuration Check"
echo "========================================="
echo ""

echo "To enable Trusted Publishing:"
echo ""
echo "1. PyPI (https://pypi.org/manage/account/publishing/):"
echo "   - PyPI Project Name: $PACKAGE_NAME"
echo "   - Owner: $(git config user.name || echo 'YOUR_GITHUB_USERNAME')"
echo "   - Repository: $(basename "$(git rev-parse --show-toplevel)")"
echo "   - Workflow: publish.yml"
echo "   - Environment: pypi"
echo ""
echo "2. TestPyPI (https://test.pypi.org/manage/account/publishing/):"
echo "   - Same settings as above"
echo "   - Environment: testpypi"
echo ""

echo "========================================="
echo "Testing Workflow Locally"
echo "========================================="
echo ""

# Test build
echo "🔨 Testing package build..."
if uv build &> /dev/null; then
   echo -e "${GREEN}✓${NC} Package built successfully"
   echo "   Files created:"
   ls -lh dist/ 2>/dev/null | tail -n +2 | awk '{print "   - " $9}'

   # Clean up
   rm -rf dist/ build/ *.egg-info 2>/dev/null
else
   echo -e "${RED}✗${NC} Build failed"
   echo "   Install build tools: pip install build"
fi

echo ""
echo "========================================="
echo "Quick Publish Commands"
echo "========================================="
echo ""

echo "Test on TestPyPI:"
echo -e "${YELLOW}  git checkout -b publish && git push origin publish${NC}"
echo ""

echo "Or manually trigger:"
echo -e "${YELLOW}  gh workflow run publish.yml -f environment=testpypi${NC}"
echo ""

echo "Publish to PyPI (create release):"
echo -e "${YELLOW}  git tag v$VERSION${NC}"
echo -e "${YELLOW}  git push origin v$VERSION${NC}"
echo -e "${YELLOW}  gh release create v$VERSION --title 'v$VERSION' --notes 'Release notes'${NC}"
echo ""

echo "========================================="
echo "Next Steps"
echo "========================================="
echo ""

echo "1. Set up Trusted Publishing on PyPI (see links above)"
echo "2. Create environments in GitHub:"
echo "   Settings → Environments → New environment"
echo "   - Create 'pypi' environment"
echo "   - Create 'testpypi' environment"
echo "3. Test workflow:"
echo "   - Push to 'publish' branch for TestPyPI"
echo "   - Create release for PyPI"
echo ""

echo -e "${GREEN}✅ Setup check complete!${NC}"
