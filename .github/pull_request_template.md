# 📋 Pull Request Description

## Summary

A brief description of what this PR does.

### Related Issues

Fixes #[issue number]
Closes #[issue number]
Related to #[issue number]

## 🎯 Type of Change

Please check the type of change your PR introduces:

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration change
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update
- [ ] 🎨 Style/formatting update

## 🔄 Changes Made

### Key Changes

- Change 1: Description
- Change 2: Description
- Change 3: Description

### Files Modified

- `file1.py` - Description of changes
- `file2.py` - Description of changes

## 💻 Code Examples

**Before:**

```python
# Old implementation
def old_method():
    pass
```

**After:**

```python
# New implementation
def new_method():
    pass
```

**Usage Example:**

```python
from nepse_client import NepseClient

client = NepseClient()
result = client.new_feature()
print(result)
```

## 🧪 Testing

### Test Coverage

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Test coverage maintained or improved

### Testing Steps

```bash
# Commands to test this PR
pytest tests/
pytest --cov=nepse_client
```

### Manual Testing

Describe any manual testing performed:

1. Step 1
2. Step 2
3. Step 3

**Test Results:**

```txt
# Test output or results
```

## 📸 Screenshots / Output

If applicable, add screenshots or sample output:

```txt
# Sample output
```

## 📚 Documentation

- [ ] Documentation updated (README, docstrings, etc.)
- [ ] CHANGELOG.md updated
- [ ] Examples updated/added
- [ ] Type hints added/updated

## ⚠️ Breaking Changes

**Does this PR introduce breaking changes?**

- [ ] No breaking changes
- [ ] Yes, breaking changes (describe below)

**If yes, describe the breaking changes and migration path:**

### Migration Guide

```python
# Old way (before this PR)
old_code()

# New way (after this PR)
new_code()
```

## 🔒 Security

- [ ] No security implications
- [ ] Security implications (describe below)

**Security Considerations:**

- Describe any security-related changes
- Mention any new dependencies and their security status

## 📊 Performance Impact

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance degraded (justify why)

**Performance Notes:**

- Benchmarks or profiling results (if applicable)

## ✅ Checklist

### Code Quality

- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Comments added for complex logic
- [ ] No commented-out code left behind

### Testing

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Edge cases covered
- [ ] Error handling tested

### Documentation

- [ ] Docstrings added/updated (Google style)
- [ ] Type hints added
- [ ] README updated (if needed)
- [ ] Examples updated/added (if needed)

### CI/CD

- [ ] All CI checks pass
- [ ] Pre-commit hooks pass
- [ ] No linting errors
- [ ] Type checking passes (mypy)
- [ ] Test coverage adequate (>80%)

### Dependencies

- [ ] No new dependencies added
- [ ] New dependencies justified and documented
- [ ] Dependencies pinned to specific versions
- [ ] `requirements.txt` updated (if needed)

## 🔗 Additional Context

Any additional information that reviewers should know:

- Design decisions made
- Alternative approaches considered
- Known limitations
- Future improvements planned

## 🙏 Reviewers

Please review:

- Code quality and style
- Test coverage
- Documentation completeness
- Breaking changes (if any)
- Performance impact

**Suggested Reviewers:** @username1, @username2

---

## 📝 Notes for Reviewers

Any specific areas you'd like reviewers to focus on:

- [ ] Algorithm efficiency in `file.py`
- [ ] Error handling in `module.py`
- [ ] API design decisions
- [ ] Documentation clarity

---

**By submitting this PR, I confirm that:**

- [ ] I have read and followed the [CONTRIBUTING.md](../CONTRIBUTING.md) guidelines
- [ ] My code follows the project's coding standards
- [ ] I have tested my changes thoroughly
- [ ] I have updated documentation as needed
- [ ] I agree to the project's license terms

---

Thank you for contributing to nepse-client! 🚀
