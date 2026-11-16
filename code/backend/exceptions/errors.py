class AppError(Exception):
    """Erreur métier de base. Toute erreur métier hérite de cette classe."""

    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    """Erreur de validation (champ manquant, format invalide, valeur hors plage…)."""

    status_code = 400


class NotFoundError(AppError):
    """Ressource inexistante."""

    status_code = 404


class ConflictError(AppError):
    """Conflit (doublon, version identique, comparaison déjà existante…)."""

    status_code = 409


class UnauthorizedError(AppError):
    """Authentification requise."""

    status_code = 401


class ForbiddenError(AppError):
    """Accès refusé."""

    status_code = 403
