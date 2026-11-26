import io
import logging
import sys
from contextlib import contextmanager
from datetime import datetime


def _ligne(niveau, source, message):
    return {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "niveau": niveau,
        "source": source,
        "message": message,
    }


class JournalHandler(logging.Handler):
    """Capture les enregistrements des loggers vers la liste `logs` du suivi."""

    def __init__(self, logs, max_lignes=1500):
        super().__init__()
        self.logs = logs
        self.max_lignes = max_lignes

    def emit(self, record):
        if len(self.logs) >= self.max_lignes:
            return
        try:
            self.logs.append(_ligne(
                record.levelname,
                record.name,
                record.getMessage(),
            ))
        except Exception:
            pass


class _Tee(io.TextIOBase):
    """Écrit à la fois vers le flux original (terminal) et dans le journal."""

    def __init__(self, original, logs, niveau, source, max_lignes):
        self._original = original
        self._logs = logs
        self._niveau = niveau
        self._source = source
        self._max_lignes = max_lignes
        self._tampon = ""

    def write(self, data):
        if self._original is not None:
            try:
                self._original.write(data)
            except Exception:
                pass
        self._tampon += data
        while "\n" in self._tampon:
            ligne, self._tampon = self._tampon.split("\n", 1)
            if ligne and len(self._logs) < self._max_lignes:
                self._logs.append(_ligne(self._niveau, self._source, ligne))
        return len(data)

    def flush(self):
        if self._original is not None:
            try:
                self._original.flush()
            except Exception:
                pass

    def isatty(self):
        return False


@contextmanager
def capturer_journal(suivi, max_lignes=1500):
    """Capture `print(..., flush=True)` (stdout/stderr) et les logs pendant un bloc.

    Les lignes sont accumulées dans ``suivi["logs"]`` (plafonné à max_lignes).
    """
    logs = suivi.setdefault("logs", [])

    handler = JournalHandler(logs, max_lignes)
    handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    racine = logging.getLogger()
    racine.addHandler(handler)

    ancien_stdout = sys.stdout
    ancien_stderr = sys.stderr
    sys.stdout = _Tee(ancien_stdout, logs, "INFO", "stdout", max_lignes)
    sys.stderr = _Tee(ancien_stderr, logs, "ERROR", "stderr", max_lignes)
    try:
        yield suivi
    finally:
        sys.stdout = ancien_stdout
        sys.stderr = ancien_stderr
        racine.removeHandler(handler)
