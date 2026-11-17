import { useState } from "react";
import { MessageCircle } from "lucide-react";
import IAChatModal from "../page/component/IAChatModal";

export default function AIAssistantButton() {
    const [open, setOpen] = useState(false);

    return (
        <>
            <button
                type="button"
                onClick={() => setOpen(true)}
                className="fixed bottom-6 right-6 z-40 flex items-center justify-center rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white p-4 shadow-[0_0_25px_rgba(6,182,212,0.45)] hover:scale-105 active:scale-95 transition-transform cursor-pointer"
                aria-label="Ouvrir la messagerie"
            >
                <MessageCircle className="w-6 h-6" />
            </button>

            {open && <IAChatModal onClose={() => setOpen(false)} />}
        </>
    );
}
