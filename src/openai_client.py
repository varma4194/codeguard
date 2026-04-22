import openai


def review_diff(diff_text: str, model: str, api_key: str) -> str:
    """
    Send a diff to OpenAI for code review.

    Args:
        diff_text: The diff text to review
        model: OpenAI model name (e.g., 'gpt-4o')
        api_key: OpenAI API key

    Returns:
        Review text from the model
    """
    client = openai.OpenAI(api_key=api_key)

    # TODO: Consider token counting for more accurate truncation
    # For now, simple character limit to avoid token overruns
    max_chars = 12000
    if len(diff_text) > max_chars:
        diff_text = diff_text[:max_chars] + "\n\n[Diff truncated due to size]"

    system_prompt = """You are an expert code reviewer. Review the provided code diff and identify:

1. **Potential Bugs**: Logic errors, edge cases, or runtime issues
2. **Security Issues**: Authentication, authorization, injection attacks, or sensitive data handling
3. **Performance Concerns**: Inefficient algorithms, N+1 queries, memory leaks, or unnecessary operations
4. **Code Quality**: Readability, maintainability, error handling, and best practices

Provide actionable feedback. Be concise but thorough. Use markdown formatting with clear sections.
If the diff is minimal or has no issues, say so explicitly."""

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"Review this code diff:\n\n{diff_text}"}
        ],
        system=system_prompt,
    )

    return message.content[0].text
