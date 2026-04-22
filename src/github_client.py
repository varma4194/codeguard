import requests
import json
from typing import list


def get_pr_diff(repo: str, pr_number: int, token: str) -> str:
    """
    Fetch the diff for a pull request.

    Args:
        repo: Repository in format 'owner/repo'
        pr_number: Pull request number
        token: GitHub API token

    Returns:
        The diff as a string
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def post_pr_comment(repo: str, pr_number: int, token: str, body: str) -> None:
    """
    Post a comment on a pull request.

    Args:
        repo: Repository in format 'owner/repo'
        pr_number: Pull request number
        token: GitHub API token
        body: Comment body (markdown)
    """
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"body": body}
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()


def get_pr_labels(repo: str, pr_number: int, token: str) -> list:
    """
    Fetch labels for a pull request.

    Args:
        repo: Repository in format 'owner/repo'
        pr_number: Pull request number
        token: GitHub API token

    Returns:
        List of label names
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return [label["name"] for label in data.get("labels", [])]
