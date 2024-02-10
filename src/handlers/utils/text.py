import logging
from bs4 import BeautifulSoup
import tiktoken

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

tokenizer = tiktoken.get_encoding("cl100k_base")  # tokenizer for ada-002 model
MAX_TOKENS = 500  # about 5 paragraphs


# replace newlines and extra spaces
def remove_newlines(text: str):
    text = text.replace("\n", " ")
    text = text.replace("\\n", " ")
    text = text.replace("  ", " ")
    text = text.replace("  ", " ")
    return text


def split_into_chunks(text: str, max_tokens=MAX_TOKENS):
    """Splits text into chunks of a maximum number of tokens"""
    sentences = text.split(". ")

    chunks: list[str] = []
    current = []
    current_tokens = 0
    # iterate through the sentences and add them to the chunk
    for sentence in sentences:
        tokens = len(tokenizer.encode(" " + sentence))

        # if the chunk is too big, add it to the chunks list
        if current_tokens + tokens > max_tokens:
            chunks.append(". ".join(current))
            current_tokens = 0
            current = []

        if tokens <= max_tokens:
            current.append(sentence)
            current_tokens += tokens + 1  # add 1 for the period

    if len(current) > 0:
        chunks.append(". ".join(current))

    return chunks


def get_text_from_html(body: str):
    """Extracts text from HTML page"""
    try:
        soup = BeautifulSoup(body, "html.parser")
        text = [p.get_text() for p in soup.find_all("p")]
        text = " ".join(text)
        return remove_newlines(text)
    except Exception as e:
        logger.error("An error occurred extracting text from HTML:", e)
        raise Exception(e)
