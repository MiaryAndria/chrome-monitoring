from backend.exceptions import ValidationError


def is_valid_datetime_range(datetime_from, datetime_to):
    if datetime_from is None or datetime_to is None:
        return True
    return datetime_to >= datetime_from


def valider_plage_datetime(datetime_from, datetime_to):
    if datetime_from is None and datetime_to is None:
        return
    if datetime_from is None:
        raise ValidationError("La date de début est manquante.")
    if datetime_to is None:
        raise ValidationError("La date de fin est manquante.")
    if datetime_to < datetime_from:
        raise ValidationError("La date/heure de début doit être antérieure ou égale à la date/heure de fin.")


__all__ = ["is_valid_datetime_range", "valider_plage_datetime"]
