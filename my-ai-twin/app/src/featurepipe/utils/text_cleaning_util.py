import re

from unstructured.cleaners.core import clean, clean_non_ascii_chars, replace_unicode_quotes


def _unbold_text_(text):
    bold_pattern = re.compile(r"[\U0001D5D4-\U0001D5ED\U0001D5EE-\U0001D607\U0001D7CE-\U0001D7FF]")
    text = bold_pattern.sub(_convert_bold_chars_, text)
    return text


def _convert_bold_chars_(text):
    # BOLD_PREFIX = '\033[1m'
    bold_numbers = {
        "\U0001D7EC": "0",
        "\U0001D7ED": "1",
        "\U0001D7EE": "2",
        "\U0001D7EF": "3",
        "\U0001D7F0": "4",
        "\U0001D7F1": "5",
        "\U0001D7F2": "6",
        "\U0001D7F3": "7",
        "\U0001D7F4": "8",
        "\U0001D7F5": "9",
    }

    char = text.group(0)
    if char in bold_numbers:
        return bold_numbers[char]
    # convert bold upper case char
    elif "\U0001d5d4" <= char <= "\U0001d5ed":
        return chr(ord(char) - 0x1D5D4 + ord("A"))
    # convert bold lower case char
    elif "\U0001d5ee" <= char <= "\U0001d607":
        return chr(ord(char) - 0x1D5EE + ord("a"))
    else :
        return char


def _unitalic_text_(text):
    """ function to convert italic chars (both letters) """

    # regex for italic chars - uppercase and lowercase
    italic_pattern = re.compile(r"[\U0001D608-\U0001D621\U0001D622-\U0001D63B]")
    text = italic_pattern.sub(_convert_italic_char_, text)
    return text


def _convert_italic_char_(text):
    """ utility that actually converts a char from italic to non-italic """
    char = text.group(0)
    if "\U0001d608" <= char <= "\U0001d621":  # Italic uppercase A-Z
        return chr(ord(char) - 0x1D608 + ord("A"))
    elif "\U0001d622" <= char <= "\U0001d63b":  # Italic lowercase a-z
        return chr(ord(char) - 0x1D622 + ord("a"))
    else:
        return char


def _remove_emojis_symbols_(text):

    emoji_and_symbol_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002193"  # downwards arrow
        "\U000021b3"  # downwards arrow with tip rightwards
        "\U00002192"  # rightwards arrow
        "]+",
        flags=re.UNICODE,
    )
    return emoji_and_symbol_pattern.sub(r" ", text)


def _replace_urls_with_placeholder_(text, placeholder="[URL]"):
    url_pattern = r"https?://\S+|www\.\S+"

    return re.sub(url_pattern, placeholder, text)



def normalize_text(text_content: str | None) -> str:
    if text_content is None:
        return ""

    cleaned_text = _unbold_text_(text_content)
    cleaned_text = _unitalic_text_(cleaned_text)
    cleaned_text = _remove_emojis_symbols_(cleaned_text)
    cleaned_text = clean(cleaned_text)
    cleaned_text = replace_unicode_quotes(cleaned_text)
    cleaned_text = clean_non_ascii_chars(cleaned_text)
    cleaned_text = _replace_urls_with_placeholder_(cleaned_text)

    return cleaned_text


# debug / test
print("printing bold zero: ", "\U0001D7CE", " also : ", "\U0001D7EC")

