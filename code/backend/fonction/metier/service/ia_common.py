import base64
import io
import os
import zipfile
import xml.etree.ElementTree as ET

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - compat environnement sans python-dotenv
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
_client = None

TAILLE_MAX_PIECE = 10 * 1024 * 1024
TAILLE_MAX_TOTALE = 18 * 1024 * 1024
MAX_PIECES = 10

MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MIME_PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
MIME_ODT = "application/vnd.oasis.opendocument.text"

MIME_NATIFS = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/heic",
    "image/heif",
    "application/pdf",
    "audio/wav",
    "audio/mp3",
    "audio/aiff",
    "audio/aac",
    "audio/ogg",
    "audio/flac",
    "video/mp4",
    "video/mpeg",
    "video/mov",
    "video/avi",
    "video/x-flv",
    "video/mpg",
    "video/webm",
    "video/wmv",
    "video/3gpp",
}

MIME_TEXTE = {
    "application/json",
    "application/xml",
    "application/yaml",
    "application/javascript",
    "application/x-javascript",
    "application/rtf",
    "image/svg+xml",
}

MIME_PAR_EXTENSION = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "heic": "image/heic",
    "heif": "image/heif",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "svg": "image/svg+xml",
    "txt": "text/plain",
    "log": "text/plain",
    "md": "text/markdown",
    "csv": "text/csv",
    "json": "application/json",
    "xml": "application/xml",
    "yaml": "application/yaml",
    "yml": "application/yaml",
    "html": "text/html",
    "htm": "text/html",
    "js": "text/javascript",
    "css": "text/css",
    "py": "text/x-python",
    "sql": "text/plain",
    "docx": MIME_DOCX,
    "xlsx": MIME_XLSX,
    "pptx": MIME_PPTX,
    "odt": MIME_ODT,
    "rtf": "application/rtf",
    "mp3": "audio/mp3",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "aac": "audio/aac",
    "mp4": "video/mp4",
    "webm": "video/webm",
    "mov": "video/mov",
    "avi": "video/avi",
}


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY manquante dans le fichier .env")
        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30_000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
    return _client


def strip_special_tokens(texte):
    for token in ("<bos>", "<eos>", "<start_of_turn>", "<end_of_turn>"):
        texte = texte.replace(token, "")
    return texte


def normaliser_mime(nom, mime):
    mime = (mime or "").strip().lower()
    if mime and mime != "application/octet-stream":
        return mime
    extension = ""
    if "." in nom:
        extension = nom.rsplit(".", 1)[-1].lower()
    if extension in MIME_PAR_EXTENSION:
        return MIME_PAR_EXTENSION[extension]
    return "application/octet-stream"


def decoder_piece_jointe(piece):
    contenu = piece.get("data") or ""
    if contenu.startswith("data:") and "," in contenu:
        contenu = contenu.split(",", 1)[1]
    try:
        return base64.b64decode(contenu, validate=False)
    except Exception:
        raise ValueError("contenu base64 invalide")


def nom_local(balise):
    return balise.rsplit("}", 1)[-1]


def extraire_texte_docx(brut):
    lignes = []
    with zipfile.ZipFile(io.BytesIO(brut)) as archive:
        contenu = archive.read("word/document.xml")
    racine = ET.fromstring(contenu)
    for element in racine.iter():
        nom = nom_local(element.tag)
        if nom == "t":
            if element.text:
                lignes.append(element.text)
        elif nom == "tab":
            lignes.append("\t")
        elif nom == "br":
            lignes.append("\n")
        elif nom == "p":
            lignes.append("\n")
    return "".join(lignes).strip()


def extraire_texte_pptx(brut):
    lignes = []
    with zipfile.ZipFile(io.BytesIO(brut)) as archive:
        for nom in archive.namelist():
            if not nom.startswith("ppt/slides/slide"):
                continue
            if not nom.endswith(".xml"):
                continue
            racine = ET.fromstring(archive.read(nom))
            for element in racine.iter():
                local = nom_local(element.tag)
                if local == "t":
                    if element.text:
                        lignes.append(element.text)
                elif local == "p":
                    lignes.append("\n")
    return "".join(lignes).strip()


def extraire_texte_odt(brut):
    lignes = []
    with zipfile.ZipFile(io.BytesIO(brut)) as archive:
        contenu = archive.read("content.xml")
    racine = ET.fromstring(contenu)
    for element in racine.iter():
        if nom_local(element.tag) != "p":
            continue
        texte = "".join(element.itertext()).strip()
        if texte:
            lignes.append(texte)
    return "\n".join(lignes)


def extraire_texte_xlsx(brut):
    from openpyxl import load_workbook

    classeur = load_workbook(io.BytesIO(brut), read_only=True, data_only=True)
    lignes = []
    for feuille in classeur.worksheets:
        lignes.append("### Feuille : " + feuille.title)
        for ligne in feuille.iter_rows(values_only=True):
            cellules = []
            vide = True
            for valeur in ligne:
                if valeur is None:
                    cellules.append("")
                else:
                    cellules.append(str(valeur))
                    vide = False
            if not vide:
                lignes.append(" | ".join(cellules))
    classeur.close()
    return "\n".join(lignes)


def texte_est_lisible(texte):
    if not texte:
        return False
    lisibles = 0
    for caractere in texte:
        if caractere.isprintable():
            lisibles += 1
        elif caractere in "\n\r\t":
            lisibles += 1
    return (lisibles / len(texte)) >= 0.9


def extraire_texte_fichier(mime, brut):
    try:
        if mime == MIME_DOCX:
            return extraire_texte_docx(brut)
        if mime == MIME_XLSX:
            return extraire_texte_xlsx(brut)
        if mime == MIME_PPTX:
            return extraire_texte_pptx(brut)
        if mime == MIME_ODT:
            return extraire_texte_odt(brut)
    except Exception:
        return ""
    if mime.startswith("text/"):
        return brut.decode("utf-8", errors="replace")
    if mime in MIME_TEXTE:
        return brut.decode("utf-8", errors="replace")
    try:
        texte = brut.decode("utf-8")
    except UnicodeDecodeError:
        return ""
    if not texte_est_lisible(texte):
        return ""
    return texte


def construire_part_fichier(nom, mime, brut):
    if mime in MIME_NATIFS:
        return types.Part.from_bytes(data=brut, mime_type=mime)
    texte = extraire_texte_fichier(mime, brut)
    if texte:
        return types.Part.from_text(
            text=(
                f"--- Début du fichier « {nom} » ({mime}) ---\n"
                f"{texte}\n"
                f"--- Fin du fichier « {nom} » ---"
            )
        )
    return types.Part.from_text(
        text=(
            f"[Pièce jointe « {nom} » : format {mime} non pris en charge "
            "et contenu illisible par l'assistant.]"
        )
    )


def construire_pieces_jointes(pieces):
    if not pieces:
        return []
    if len(pieces) > MAX_PIECES:
        raise ValueError(f"Trop de pièces jointes (maximum {MAX_PIECES} par message).")

    parts = []
    noms = []
    total = 0
    for piece in pieces:
        nom = (piece.get("name") or "fichier").strip() or "fichier"
        mime = normaliser_mime(nom, piece.get("mime_type"))
        try:
            brut = decoder_piece_jointe(piece)
        except ValueError as erreur:
            parts.append(
                types.Part.from_text(text=f"[Pièce jointe « {nom} » ignorée : {erreur}.]")
            )
            continue
        if not brut:
            parts.append(
                types.Part.from_text(text=f"[Pièce jointe « {nom} » ignorée : fichier vide.]")
            )
            continue
        if len(brut) > TAILLE_MAX_PIECE:
            parts.append(
                types.Part.from_text(
                    text=(
                        f"[Pièce jointe « {nom} » ignorée : "
                        f"dépasse {TAILLE_MAX_PIECE // (1024 * 1024)} Mo.]"
                    )
                )
            )
            continue
        total = total + len(brut)
        if total > TAILLE_MAX_TOTALE:
            parts.append(
                types.Part.from_text(
                    text=(
                        f"[Pièce jointe « {nom} » ignorée : total des pièces jointes "
                        f"supérieur à {TAILLE_MAX_TOTALE // (1024 * 1024)} Mo.]"
                    )
                )
            )
            continue
        parts.append(construire_part_fichier(nom, mime, brut))
        noms.append(nom)

    if not noms:
        return parts
    entete = types.Part.from_text(
        text=(
            "PIÈCES JOINTES FOURNIES PAR L'UTILISATEUR : "
            + ", ".join(noms)
            + ". Analyse leur contenu réel et appuie ta réponse dessus."
        )
    )
    return [entete] + parts


def construire_parts_message(message):
    texte = (message.get("content") or "").strip()
    pieces = message.get("attachments") or []
    parts = []
    if texte:
        parts.append(types.Part.from_text(text=texte))
    if pieces:
        if not texte:
            parts.append(
                types.Part.from_text(text="Analyse les pièces jointes fournies.")
            )
        parts.extend(construire_pieces_jointes(pieces))
    return parts
