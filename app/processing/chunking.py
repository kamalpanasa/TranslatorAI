import re
from typing import List


def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using regex.
    Handles basic punctuation sentence boundaries (., !, ?).
    """
    if not text:
        return []
    # Split using punctuation followed by whitespace. Keep the punctuation with the sentence.
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """
    Chunks text into blocks of max_chars size, preserving sentence boundaries.
    If a single sentence exceeds max_chars, it will be chunked by word/char.
    """
    if not text:
        return []

    sentences = split_into_sentences(text)
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_length = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        
        # If a single sentence exceeds max_chars by itself
        if sentence_len > max_chars:
            # First, flush the current chunk if it has content
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            
            # Split the long sentence by words to fit within max_chars
            words = sentence.split(" ")
            sub_chunk: List[str] = []
            sub_len = 0
            for word in words:
                word_len = len(word) + 1  # include space
                if sub_len + word_len > max_chars:
                    if sub_chunk:
                        chunks.append(" ".join(sub_chunk))
                    sub_chunk = [word]
                    sub_len = word_len
                else:
                    sub_chunk.append(word)
                    sub_len += word_len
            if sub_chunk:
                chunks.append(" ".join(sub_chunk))
            continue

        if current_length + sentence_len + 1 > max_chars:
            # Flush current chunk
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_length = sentence_len
        else:
            current_chunk.append(sentence)
            current_length += sentence_len + (1 if current_length > 0 else 0)

    # Append any remaining text
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
