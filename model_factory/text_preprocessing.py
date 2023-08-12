import re
import Stemmer


RU_STEMMER = Stemmer.Stemmer("ru")
TABS_REGEXP = re.compile(r"[\n\t\r]+")
TAGS_REGEXP = re.compile(r"(\<(/?[^>]+)>)")
SYMBOLS_REGEXP = re.compile(r"[^a-zа-я0-9]")
SPACES_REGEXP = re.compile(r"\s+")
HTML_REGEXP = re.compile(r"(\<(/?[^>]+)>)")


def clean_html(text: str) -> str:
    text = HTML_REGEXP.sub(" ", text)
    return SPACES_REGEXP.sub(" ", text).strip()


def text_cleanup_preprocessor(text: str) -> str:
    result = clean_html(str(text))
    result = result.lower()
    result = result.replace("ё", "е")
    result = TABS_REGEXP.sub(" ", result)
    result = TAGS_REGEXP.sub(" ", result)
    result = SYMBOLS_REGEXP.sub(" ", result)
    result = result.strip()
    result = SPACES_REGEXP.sub(" ", result)
    return " ".join([RU_STEMMER.stemWord(word) for word in result.split()])


def text_cleanup(texts):
    return [text_cleanup_preprocessor(text) for text in texts]
