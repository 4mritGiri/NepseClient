---
name: Bug Report
about: Create a report to help us improve nepse-client
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug Description

A clear and concise description of what the bug is.

## 🔄 Steps To Reproduce

Steps to reproduce the behavior:

1. Initialize client with '...'
2. Call method '....'
3. Pass parameters '....'
4. See error

## 💡 Expected Behavior

A clear and concise description of what you expected to happen.

## ❌ Actual Behavior

A clear and concise description of what actually happened.

## 📝 Code Sample

```python
# Minimal code to reproduce the issue
from nepse_client import NepseClient

client = NepseClient()
# Your code here that triggers the bug
```

## 📋 Error Message / Traceback

```python
# Full error message and traceback
Traceback (most recent call last):
  File "...", line ..., in ...
    ...
Error: ...
```

## 🖥️ Environment

**System Information:**

- OS: [e.g., Ubuntu 22.04, Windows 11, macOS 14]
- Python Version: [e.g., 3.10.5]
- nepse-client Version: [e.g., 1.0.0]
- Installation Method: [e.g., pip, uv, poetry]

**Dependencies:**

```bash
# Output of: pip list | grep -E "httpx|pywasm|tqdm"
httpx==0.28.1
pywasm==2.2.1
tqdm==4.67.1
```

## 📸 Screenshots

If applicable, add screenshots to help explain your problem.

## 🔍 Additional Context

Add any other context about the problem here:

- Does this happen consistently or intermittently?
- Did this work in a previous version?
- Any network/firewall configurations?
- Are you using sync or async client?

## ✅ Checklist

- [ ] I have searched for similar issues before creating this one
- [ ] I have provided a minimal code example that reproduces the issue
- [ ] I have included the full error traceback
- [ ] I have specified my environment details
- [ ] I am using the latest version of nepse-client

## 🤝 Willing to Submit a PR?

- [ ] Yes, I'd like to work on fixing this issue
- [ ] No, but I'm happy to help test a fix

---

**Note:** Please ensure you're using the latest version of nepse-client before submitting a bug report. You can upgrade with:

```bash
pip install --upgrade nepse-client
```
