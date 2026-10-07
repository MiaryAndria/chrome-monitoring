import { useState, useEffect } from "react";

export function useMouseSpotlight() {
    const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleMouseMove = (e) => {
            setCursorPos({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    return {
        style: {
            '--mouse-x': `${cursorPos.x}px`,
            '--mouse-y': `${cursorPos.y}px`
        }
    };
}
