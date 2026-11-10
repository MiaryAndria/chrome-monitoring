import { useState } from "react";
import { Bot } from "lucide-react";
import IAChatModal from "../page/component/IAChatModal";

export default function AIAssistantButton() {
    const [open, setOpen] = useState(false);

    return (
        <>
            <button
                type="button"
                onClick={() => setOpen(true)}
                className="fixed bottom-6 right-6 z-40 flex items-center gap-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-4 py-3 text-sm font-semibold shadow-[0_0_25px_rgba(6,182,212,0.45)] hover:scale-105 active:scale-95 transition-transform cursor-pointer"
                aria-label="Ouvrir l'assistant IA"
            >
                <Bot className="w-5 h-5" />
                <span className="hidden sm:inline">Assistant IA</span>
            </button>

            {open && <IAChatModal onClose={() => setOpen(false)} />}
        </>
    );
}
