# CodeGuard - AI-Powered Code Review

A lightweight GitHub Action that uses OpenAI's GPT-4o to review pull request diffs and post structured feedback on security, performance, and code quality.

## Features

- Automatically reviews PRs on `pull_request` events
- Analyzes code for bugs, security issues, performance concerns, and code quality
- Posts review as a GitHub comment
- Skips large PRs (configurable file limit)
- Respects `skip-ai-review` label to opt out
- Clean error handling and logging

## Setup

### 1. Add the Action to Your Repo

Create `.github/workflows/codeguard.yml` in your repository:

```yaml
name: CodeGuard Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  codeguard:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Run CodeGuard AI Review
        uses: <your-repo>/codeguard@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
```

### 2. Add OpenAI API Key

1. Go to your repository **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `OPENAI_API_KEY`
4. Value: Your OpenAI API key (get one at https://platform.openai.com/api-keys)

### 3. Grant Permissions

The action needs permission to:
- Read PR contents
- Write PR comments

Most workflows include this automatically via `pull-requests: write`.

## Configuration

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `github-token` | Yes | — | GitHub token (usually `secrets.GITHUB_TOKEN`) |
| `openai-api-key` | Yes | — | OpenAI API key |
| `model` | No | `gpt-4o` | OpenAI model to use |
| `max-files` | No | `10` | Skip review if PR exceeds this file count |
| `skip-label` | No | `skip-ai-review` | Label to skip AI review |

### Example: Custom Configuration

```yaml
- name: Run CodeGuard AI Review
  uses: your-repo/codeguard@main
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    model: gpt-4o
    max-files: 20
    skip-label: no-review
```

## Review Output

CodeGuard posts a structured comment with sections for:

- **Potential Bugs**: Logic errors, edge cases, runtime issues
- **Security Issues**: Auth, injection attacks, sensitive data handling
- **Performance Concerns**: Inefficient code, memory issues
- **Code Quality**: Readability, maintainability, error handling

Example:

```
## CodeGuard AI Review

### Potential Bugs
- The `validate_user()` function doesn't handle null inputs

### Security Issues
- No validation on user input in the email field

### Performance Concerns
- Consider indexing the `user_id` column in queries

### Code Quality
- Good error handling overall, but consider logging the full exception

---
*Review powered by CodeGuard and gpt-4o*
```

## Skipping Reviews

Add the `skip-ai-review` label to a PR to skip the CodeGuard review (or configure a custom label).

## Cost

CodeGuard uses the OpenAI API, which incurs costs based on token usage. A typical PR review costs $0.01–$0.10 depending on diff size and model.

## Limitations

- PRs larger than `max-files` are skipped (default: 10 files)
- Diffs are truncated to ~12,000 characters to manage token usage
- The review is advisory; always review code yourself
- Requires valid OpenAI API credentials

## Error Handling

If the OpenAI API fails, CodeGuard posts an error comment instead of silently failing. Check the action logs for details.

## License

MIT
