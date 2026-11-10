from google.genai import errors, types

from backend.fonction.metier.service.ia_common import (
    MODEL,
    get_client,
    strip_special_tokens,
)

GENERAL_SYSTEM_PROMPT = """Tu es l'assistant IA intégré à une application de supervision de parc de Chromebooks (ChromeOS / Chrome Enterprise). Tu aides les administrateurs et techniciens.

Format obligatoire (lisibilité avant tout) :
- Commence TOUJOURS par une section "## En bref" : 3 à 5 puces maximum.
- Ensuite, développe dans des sections "## Titre court" (2 à 5 maximum).
- Paragraphes de 2 à 3 phrases maximum ; listes à puces ; mots-clés en gras.
- Termine par "## À faire maintenant" avec une action prioritaire.
- N'utilise pas de tableaux.

Contenu :
- Réponds en français, de façon claire et pédagogique.
- Tu peux répondre sur ChromeOS, les crashes, la maintenance, la gestion d'un parc d'appareils et l'utilisation de l'application.
- Pour une analyse précise d'un événement ou d'un appareil, indique que l'utilisateur peut ouvrir l'événement puis cliquer sur "Demander à l'IA" pour que les données exactes soient disponibles ; sinon demande-lui les informations utiles.
- Si une information manque, dis-le. Ne révèle jamais de secrets.
"""


def _build_contents(messages):
    contents = []
    for message in messages:
        role = "model" if message.get("role") == "assistant" else "user"
        texte = (message.get("content") or "").strip()
        if not texte:
            continue
        contents.append({"role": role, "parts": [{"text": texte}]})

    if not contents:
        contents.append({
            "role": "user",
            "parts": [{"text": "Posez votre question sur ChromeOS ou le parc d'appareils."}],
        })
    return contents


def _build_config():
    return types.GenerateContentConfig(
        system_instruction=GENERAL_SYSTEM_PROMPT,
        temperature=0.3,
        max_output_tokens=8192,
        thinking_config=types.ThinkingConfig(thinking_level="low"),
    )


def stream_general_chat(messages):
    """Génère la réponse de l'assistant général par morceaux (streaming)."""
    try:
        stream = get_client().models.generate_content_stream(
            model=MODEL,
            contents=_build_contents(messages),
            config=_build_config(),
        )
        for chunk in stream:
            texte = getattr(chunk, "text", None)
            if texte:
                texte = strip_special_tokens(texte)
                if texte:
                    yield texte
    except errors.APIError as e:
        code = getattr(e, "code", "?")
        yield (
            f"\n\n[Le service IA est momentanément indisponible (code {code}). "
            "Réessayez dans un instant.]"
        )
    except Exception as e:  # pragma: no cover - garde-fou streaming
        yield f"\n\n[Erreur pendant la génération : {e}]"
