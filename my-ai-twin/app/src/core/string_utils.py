from core.errors import ImproperlyConfigured


def split_user_full_name(user:str | None) -> tuple[str, str]:

    if (not user):
        raise ImproperlyConfigured("User name is required to split the full name")

    name_tokens = user.split(" ")

    if len(name_tokens) == 1:
        return name_tokens[0], name_tokens[0]
    else:
        return " ".join(name_tokens[:-1]), name_tokens[-1]


def flatten_nested_list(nested_list: list) -> list :
    """Given a nested list (list of lists), returns a single list

    Args:
        nested_list (list): list of lists

    Returns:
        list: a single list
    """

    return [item
            for sublist in nested_list
                for item in sublist]

