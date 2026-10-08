from app.agentt.retry import LLMRetryableError


def classify_llm_error(error: Exception) -> Exception:
    message = str(error).lower()

    retryable_messages = (
        "connection",
        "connect",
        "timeout",
        "timed out",
        "temporarily unavailable",
        "server error",
        "internal server error",
        "service unavailable",
    )

    if any(
        text in message
        for text in retryable_messages
    ):
        return LLMRetryableError(
            f"LLM temporarily unavailable: {error}"
        )

    return error