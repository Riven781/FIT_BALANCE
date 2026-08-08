POLISH_CHARS = {
    "ą": "a",
    "ć": "c",
    "ę": "e",
    "ł": "l",
    "ń": "n",
    "ó": "o",
    "ś": "s",
    "ż": "z",
    "ź": "z",
    "Ą": "A",
    "Ć": "C",
    "Ę": "E",
    "Ł": "L",
    "Ń": "N",
    "Ó": "O",
    "Ś": "S",
    "Ż": "Z",
    "Ź": "Z",
}


def normalize_for_search(text: str):
  return text.lower().translate(str.maketrans(POLISH_CHARS))

def tokenize_for_search(text: str):
  return normalize_for_search(text).split()