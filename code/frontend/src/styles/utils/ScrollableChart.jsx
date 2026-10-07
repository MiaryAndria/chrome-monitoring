import { useRef, useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

function ScrollableChart({ children }) {
    const scrollRef = useRef(null);
    const [canScrollLeft, setCanScrollLeft] = useState(false);
    const [canScrollRight, setCanScrollRight] = useState(false);
    const [showHint, setShowHint] = useState(true);

    const updateScrollState = () => {
        const el = scrollRef.current;
        if (!el) return;
        setCanScrollLeft(el.scrollLeft > 4);
        setCanScrollRight(el.scrollLeft < el.scrollWidth - el.clientWidth - 4);
    };

    useEffect(() => {
        updateScrollState();
        const el = scrollRef.current;
        if (!el) return;
        el.addEventListener('scroll', updateScrollState);
        window.addEventListener('resize', updateScrollState);
        return () => {
            el.removeEventListener('scroll', updateScrollState);
            window.removeEventListener('resize', updateScrollState);
        };
    }, []);

    const scrollBy = (dir) => {
        scrollRef.current?.scrollBy({ left: dir * 240, behavior: 'smooth' });
        setShowHint(false);
    };

    return (
        <div className="relative">
            {/* Dégradés indiquant qu'il y a plus de contenu */}
            {canScrollLeft && (
                <div className="pointer-events-none absolute left-0 top-0 bottom-0 w-10 z-10 bg-gradient-to-r from-zinc-900/80 to-transparent" />
            )}
            {canScrollRight && (
                <div className="pointer-events-none absolute right-0 top-0 bottom-0 w-10 z-10 bg-gradient-to-l from-zinc-900/80 to-transparent" />
            )}

            {/* Flèches cliquables */}
            {canScrollLeft && (
                <button
                    onClick={() => scrollBy(-1)}
                    className="absolute left-1 top-1/2 -translate-y-1/2 z-20 p-1.5 rounded-full bg-zinc-800/90 border border-white/10 text-zinc-300 hover:text-cyan-400 hover:border-cyan-500/30 transition-all shadow-lg"
                    aria-label="Défiler vers la gauche"
                >
                    <ChevronLeft className="w-4 h-4" />
                </button>
            )}
            {canScrollRight && (
                <button
                    onClick={() => scrollBy(1)}
                    className="absolute right-1 top-1/2 -translate-y-1/2 z-20 p-1.5 rounded-full bg-zinc-800/90 border border-white/10 text-zinc-300 hover:text-cyan-400 hover:border-cyan-500/30 transition-all shadow-lg"
                    aria-label="Défiler vers la droite"
                >
                    <ChevronRight className="w-4 h-4" />
                </button>
            )}

            <div
                ref={scrollRef}
                onScroll={() => setShowHint(false)}
                className="overflow-x-auto no-scrollbar scroll-smooth"
            >
                {children}
            </div>

            {/* Indice discret la première fois, seulement s'il y a du contenu caché */}
            {canScrollRight && showHint && (
                <div className="flex items-center justify-center gap-1.5 mt-1.5 text-[10px] text-zinc-500 animate-pulse">
                    <ChevronLeft className="w-3 h-3" />
                    Faites glisser pour voir plus
                    <ChevronRight className="w-3 h-3" />
                </div>
            )}
        </div>
    );
}

export default ScrollableChart;