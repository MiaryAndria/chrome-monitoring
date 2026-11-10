const API_BASE_URL = "http://localhost:8000";

export const IAChatGlobalStream = async (messages, onChunk, signal) => {
    const response = await fetch(`${API_BASE_URL}/ia/chat/stream`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages }),
        signal,
    });

    if (response.status === 401) {
        window.location.href = "/login";
        throw new Error("Session expirée, reconnectez-vous.");
    }

    if (!response.ok) {
        let detail = `Erreur ${response.status}`;
        try {
            const data = await response.json();
            detail = data.detail || detail;
        } catch (e) {
            // réponse non JSON
        }
        throw new Error(detail);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let texte = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const morceau = decoder.decode(value, { stream: true });
        if (morceau) {
            texte += morceau;
            onChunk(morceau, texte);
        }
    }

    const reste = decoder.decode();
    if (reste) {
        texte += reste;
        onChunk(reste, texte);
    }

    return texte;
};
