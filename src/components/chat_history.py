def messages_for_display(messages, analysis_result):
    """Avoid displaying the already-rendered analysis twice while keeping history intact."""
    skipped_analysis = False
    for message in messages:
        if (
            not skipped_analysis
            and message.get("role") == "assistant"
            and message.get("content") == analysis_result
        ):
            skipped_analysis = True
            continue
        yield message
