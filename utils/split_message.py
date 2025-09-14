import re

def split_message(text, chunk_size=4000):
    """
    Splits a long text into chunks for sending via Telegram.

    This function takes a long text and breaks it into several parts (chunks)
    so that they can be sent to Telegram, as Telegram has a limit on the length
    of a single message. The splitting occurs by sentences to avoid
    breaking sentences in the middle.

    Args:
        text (str): The original text to split.
        chunk_size (int, optional): The maximum chunk size. Defaults to 4000 characters.
                                    This value is chosen because Telegram's limit is 4096 characters,
                                    leaving a small buffer.

    Returns:
        list[str]: A list of text chunks. Each chunk is a string
                     that does not exceed chunk_size in length.
    """
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    current_chunk = ""
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks