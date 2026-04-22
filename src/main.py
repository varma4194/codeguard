#!/usr/bin/env python3
"""
CodeGuard - AI-powered code review GitHub Action.

Fetches PR diff, sends to OpenAI, posts review as a GitHub comment.
"""

import json
import os
import sys
from pathlib import Path

from github_client import get_pr_diff, get_pr_labels, post_pr_comment
from openai_client import review_diff


def get_pr_info():
    """
    Extract PR info from GitHub event payload.

    Returns:
        (repo, pr_number) tuple or exits if not a PR event
    """
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        print("ERROR: GITHUB_EVENT_PATH not set or file not found")
        sys.exit(1)

    with open(event_path) as f:
        event = json.load(f)

    # Check if this is a pull_request event
    if "pull_request" not in event:
        print("INFO: Not a pull request event, skipping")
        sys.exit(0)

    pr = event["pull_request"]
    repo = event["repository"]["full_name"]
    pr_number = pr["number"]

    return repo, pr_number


def should_skip_review(labels: list, skip_label: str) -> bool:
    """Check if PR has the skip label."""
    return skip_label in labels


def split_diff_by_file(diff_text: str) -> list:
    """
    Split diff into per-file chunks.

    Simple parsing: each 'diff --git' line marks a new file.

    Returns:
        List of (filename, file_diff) tuples
    """
    files = []
    current_file = None
    current_diff = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            # Extract filename from "diff --git a/path b/path"
            parts = line.split(" ")
            if len(parts) >= 4:
                # Take the 'b/path' part and strip the 'b/'
                filename = parts[3][2:]
                if current_file:
                    files.append((current_file, "\n".join(current_diff)))
                current_file = filename
                current_diff = [line]
            else:
                current_diff.append(line)
        else:
            if current_file is not None:
                current_diff.append(line)

    if current_file:
        files.append((current_file, "\n".join(current_diff)))

    return files


def main():
    """Main execution."""
    # Load config from environment
    github_token = os.getenv("GITHUB_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL", "gpt-4o")
    max_files = int(os.getenv("MAX_FILES", "10"))
    skip_label = os.getenv("SKIP_LABEL", "skip-ai-review")

    if not github_token or not openai_api_key:
        print("ERROR: GITHUB_TOKEN and OPENAI_API_KEY required")
        sys.exit(1)

    # Get PR info
    repo, pr_number = get_pr_info()
    print(f"Reviewing PR {repo}#{pr_number}")

    # Check skip label
    labels = get_pr_labels(repo, pr_number, github_token)
    if should_skip_review(labels, skip_label):
        print(f"INFO: PR has '{skip_label}' label, skipping review")
        sys.exit(0)

    # Fetch diff
    try:
        diff_text = get_pr_diff(repo, pr_number, github_token)
    except Exception as e:
        print(f"ERROR: Failed to fetch PR diff: {e}")
        sys.exit(1)

    if not diff_text.strip():
        print("INFO: No diff found, skipping review")
        sys.exit(0)

    # Check file count
    files = split_diff_by_file(diff_text)
    if len(files) > max_files:
        message = (
            f"PR too large ({len(files)} files). "
            f"CodeGuard skips reviews for PRs with more than {max_files} files."
        )
        try:
            post_pr_comment(repo, pr_number, github_token, message)
        except Exception as e:
            print(f"WARNING: Failed to post skip message: {e}")
        print(f"INFO: {message}")
        sys.exit(0)

    # Generate review
    print(f"Sending diff to {model} for review...")
    try:
        review = review_diff(diff_text, model, openai_api_key)
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}")
        error_message = (
            f"CodeGuard AI review failed: {str(e)}\n\n"
            "Please check the action logs for details."
        )
        try:
            post_pr_comment(repo, pr_number, github_token, error_message)
        except Exception as post_err:
            print(f"ERROR: Also failed to post error message: {post_err}")
        sys.exit(1)

    # Post review
    comment_body = f"""## CodeGuard AI Review

{review}

---
*Review powered by CodeGuard and {model}*"""

    try:
        post_pr_comment(repo, pr_number, github_token, comment_body)
        print("✓ Review posted successfully")
    except Exception as e:
        print(f"ERROR: Failed to post review comment: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
