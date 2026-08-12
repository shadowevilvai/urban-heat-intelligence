# Urban Heat Intelligence — Team Start Here

## Purpose

This document is the first thing every team member should read before coding.

We use one GitHub repository and separate branches. Nobody should exchange project folders by WhatsApp/Drive or copy another person's code manually.

### Team model

```text
                         GitHub Repository
                               |
                    +----------+----------+
                    |                     |
                  develop                main
                    |
        +-----------+-----------+-----------+-----------+
        |           |           |           |           |
    frontend     backend       ml       geospatial  optimization
      branch      branch      branch       branch       branch
```

`main` = stable/demo-ready code.

`develop` = integration branch.

Each person works on a feature branch created from `develop`.

---

## Before You Start

Ask the team lead for:

1. GitHub repository URL
2. GitHub access
3. The current `develop` branch
4. The current API contract
5. Required `.env` values
6. Development database instructions
7. The exact project stack/version if it has changed from this guide

Never ask someone to send their entire project folder.

---

## Golden Rules

1. **Never push directly to `main`.**
2. **Never push directly to `develop` unless the team lead explicitly asks you to.**
3. Work on your own feature branch.
4. Pull the latest `develop` before starting new work.
5. Keep commits small and meaningful.
6. Open a Pull Request when your feature is ready.
7. Do not change API request/response formats without informing the people who use them.
8. Never commit `.env`, passwords, API keys, database credentials, model secrets, or private files.
9. Do not commit huge generated datasets, caches, build folders, virtual environments, or `node_modules`.
10. If you get a merge conflict, stop and resolve it carefully. Do not randomly delete one side.

GitHub's documented collaboration model is based on branches and pull requests, which allows changes to be isolated and reviewed before merging.
