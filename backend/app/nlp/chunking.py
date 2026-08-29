import re

# matches whitespace that comes right after a period, exclamation mark, or question mark
# this is a simple rule based splitter, not a real sentence tokenizer, so it will get
# things like "13.3 inch" wrong sometimes. that is an acceptable tradeoff here since a
# wrong split just means a slightly odd sized chunk, not a broken pipeline
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    sentences = SENTENCE_END.split(text.strip())
    return [s for s in sentences if s]  # drop empty strings from the split


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    sentences = split_sentences(text)
    chunks = []
    current = ""

    for sentence in sentences:
        # adding this sentence would push the current chunk over the limit,
        # so close out the current chunk and start a new one with this sentence
        if current and len(current) + len(sentence) + 1 > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()

    if current:
        chunks.append(current)  # add whatever is left after the loop ends

    return chunks
