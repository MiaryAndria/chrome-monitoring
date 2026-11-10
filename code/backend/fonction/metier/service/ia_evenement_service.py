import json

from google.genai import errors, types

from backend.fonction.metier.service.ia_common import (
    MODEL,
    get_client,
    strip_special_tokens,
)

SYSTEM_PROMPT = """Tu es un ingénieur de support expert en supervision de parc de Chromebooks (ChromeOS / Chrome Enterprise). Tu produis des analyses techniques approfondies, mais toujours lisibles et faciles à parcourir.

Format obligatoire (lisibilité avant tout) :
- Commence TOUJOURS par une section "## En bref" : 3 à 5 puces maximum résumant l'essentiel (cause la plus probable + action prioritaire). C'est ce que l'utilisateur lit en premier.
- Ensuite seulement, développe les détails dans des sections "## Titre court" (2 à 5 sections maximum).
- Paragraphes de 2 à 3 phrases maximum : jamais de pavés de texte.
- Privilégie les listes à puces pour les causes et les étapes ; mets en gras les mots-clés importants.
- Termine par "## À faire maintenant" : une seule action prioritaire, en une phrase claire.
- N'utilise pas de tableaux (non affichés). Évite les répétitions et le remplissage.

Contenu :
- Réponds en français, avec un haut niveau de détail mais sans verbiage.
- Appuie chaque affirmation sur les données fournies et cite les champs utilisés (ex. minutes_since_boot, crash_seq, cause_class).
- Pour chaque cause possible : mécanisme technique, indices qui la soutiennent, et vérification concrète.
- Donne des procédures étape par étape avec le résultat attendu.
- Si une information manque, dis-le explicitement. Ne révèle jamais de secrets, clés ou identifiants.
- Reste dans le domaine du diagnostic et de la maintenance des appareils.
- Longueur cible : 400 à 800 mots pour une analyse complète. Si c'est plus long, condense.
"""


def _parse_details(details):
    if isinstance(details, str):
        try:
            return json.loads(details)
        except Exception:
            return {}
    return details or {}


def _build_event_context(evenement):
    details = _parse_details(evenement.get("details"))
    date_evenement = evenement.get("date_evenement")

    return f"""DONNÉES DE L'ÉVÉNEMENT À ANALYSER
- ID événement      : {evenement.get("id")}
- Date              : {date_evenement}
- Type d'événement  : {evenement.get("type_evenement")}
- Appareil          : {evenement.get("modele") or "inconnu"}
- Numéro de série   : {evenement.get("serial_number") or "inconnu"}
- Device ID         : {evenement.get("device_id") or "inconnu"}
- Filiale           : {evenement.get("filiale") or "inconnue"}
- Cause class       : {details.get("cause_class") or "non précisée"}
- Indice de cause   : {details.get("cause_hint") or "aucun"}
- Dernier utilisateur : {details.get("last_user") or "inconnu"}
- Clé d'incident    : {details.get("incident_key") or "aucune"}
- Séquence de crash : {details.get("crash_seq")}
- Événements bruts  : {details.get("raw_events")}
- Minutes depuis boot : {details.get("minutes_since_boot")}

Détails techniques complets (JSON) :
{json.dumps(details, ensure_ascii=False, indent=2)}
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
            "parts": [{"text": "Analyse cet événement et explique la cause probable."}],
        })
    return contents


def _build_config(contexte):
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT + "\n\n" + contexte,
        temperature=0.3,
        max_output_tokens=8192,
        thinking_config=types.ThinkingConfig(thinking_level="low"),
    )


def stream_chat_with_ia(evenement, messages):
    """Génère l'analyse de l'événement par morceaux (streaming)."""
    contexte = _build_event_context(evenement)
    try:
        stream = get_client().models.generate_content_stream(
            model=MODEL,
            contents=_build_contents(messages),
            config=_build_config(contexte),
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
