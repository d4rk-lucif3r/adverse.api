# Security Guidelines

This document outlines security guidelines for handling sensitive data in this repository.

## Sensitive Data Handling

### Identifying Sensitive Data

The following are considered sensitive data that should not be committed to the repository:

- API keys and tokens
- Database credentials
- Passwords and secrets
- Connection strings
- Personal identifiable information (PII)

### MongoDB ObjectIDs

MongoDB ObjectIDs should be masked in any backup or exported data files to prevent false positives in security scans. The format of a MongoDB ObjectID is a 24-character hexadecimal string.

Example of masking:
- Original: `"$oid": "61c07e50e6bcdfdcb3f3d889"`
- Masked: `"$oid": "61********************89"`

### Utilities Provided

This repository includes utilities to help maintain security best practices:

1. `backup_data/sanitize_backup_data.py` - Script to sanitize MongoDB ObjectIDs in backup data files
2. `scan_sensitive_data.py` - Script to scan the repository for potential sensitive data

### Usage

To sanitize backup data:

```bash
python backup_data/sanitize_backup_data.py
```

To scan for sensitive data:

```bash
python scan_sensitive_data.py
```

## Best Practices

1. Never commit sensitive data to the repository
2. Use environment variables for secrets in development and production
3. Sanitize data exports and backups before committing
4. Regularly scan the codebase for potential sensitive data leaks
5. Use a .gitignore file to prevent accidentally committing sensitive files

## Reporting Security Issues

If you discover a security vulnerability in this repository, please report it responsibly by contacting the repository owner.