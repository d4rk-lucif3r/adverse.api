# Security Guidelines

## Handling Sensitive Data

To ensure the security of this application, please follow these guidelines:

1. **Never commit sensitive data** such as API keys, passwords, or personal information to the repository.

2. **Environment variables**: Store all sensitive information in environment variables.
   - Copy `.env.example` to `.env` (which is gitignored)
   - Add your actual secrets to `.env`
   - Access these variables in your code, don't hardcode secrets

3. **MongoDB ObjectIDs**: Be aware that some ObjectIDs may contain sensitive information. Always redact or mask these IDs when logging or storing them in files that might be committed.

4. **Backup data**: The `/backup_data` directory may contain sensitive information. Files in this directory should be properly sanitized before committing.

5. **Security reviews**: Perform regular security audits of your code to identify and fix potential vulnerabilities.

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly by contacting the security team.