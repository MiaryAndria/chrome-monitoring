def is_valid_datetime_range(datetime_from, datetime_to):
    if datetime_from is None or datetime_to is None:
        return True
    return datetime_to >= datetime_from


__all__ = ["is_valid_datetime_range"]
