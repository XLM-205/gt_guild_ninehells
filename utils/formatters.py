def format_abbreviated_number(number: int) -> str:
    if number > 1_000_000_000_000:
        return f"{int(number / 1_000_000_000_000)}T"
    elif number > 1_000_000_000:
        return f"{int(number / 1_000_000_000)}B"
    elif number > 1_000_000:
        return f"{int(number / 1_000_000)}M"
    elif number > 1_000:
        return f"{int(number / 1_000)}K"
    else:
        return f"{int(number)}"