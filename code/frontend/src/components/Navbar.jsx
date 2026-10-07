import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, User, Sun, Moon } from 'lucide-react';

export default function Navbar() {
    const navigate = useNavigate();
    const [parametre, setParametre] = useState('');
    const [isLightMode, setIsLightMode] = useState(false);

    useEffect(() => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme === 'light') {
            setIsLightMode(true);
            applyTheme('light');
        } else {
            setIsLightMode(false);
            applyTheme('dark');
        }
    }, []);

    const applyTheme = (theme) => {
        // Applique le thème à tous les conteneurs layout
        document.querySelectorAll('.device-layout').forEach(el => {
            el.setAttribute('data-theme', theme);
        });
    };

    const toggleTheme = () => {
        const newTheme = isLightMode ? 'dark' : 'light';
        setIsLightMode(!isLightMode);
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            if (parametre.trim()) {
                navigate(`/liste/device?search=${encodeURIComponent(parametre.trim())}`);
            } else {
                navigate('/liste/device');
            }
        }
    };

    return (
        <div className="header-container glass-panel">
            <div className="flex items-center gap-4">
                <h1 className="text-xl font-semibold text-zinc-100 hidden sm:block">Dashboard</h1>
            </div>

            <div className="flex items-center gap-6">
                <div className="relative hidden md:block">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                    <input 
                        type="text" 
                        value={parametre}
                        onChange={(e) => setParametre(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Rechercher (S/N, Modèle, IP, Email)..."
                        className="input input-sm input-bordered bg-zinc-900/50 border-zinc-800 text-zinc-300 w-72 pl-9 focus:border-cyan-500/50 focus:outline-none transition-all"
                    />
                </div>

                <div className="flex items-center gap-5">
                    {/* Interrupteur Light/Dark Mode (Style Mural Horizontal, Petite Taille) */}
                    <button 
                        onClick={toggleTheme}
                        title="Basculer le thème"
                        className={`relative w-12 h-6 rounded border border-zinc-900 overflow-hidden shadow-[0_2px_5px_rgba(0,0,0,0.5)] flex items-center cursor-pointer ${isLightMode ? 'bg-zinc-300' : 'bg-zinc-800'}`}
                    >
                        {/* Gauche (ON) */}
                        <div className={`flex-1 h-full flex items-center justify-start pl-1.5 transition-colors ${isLightMode ? 'bg-zinc-200' : 'bg-zinc-700/50'}`}>
                            <span className={`text-[8px] font-black ${isLightMode ? 'text-zinc-600' : 'text-zinc-500'}`}>ON</span>
                        </div>
                        {/* Droite (OFF) */}
                        <div className={`flex-1 h-full flex items-center justify-end pr-1 transition-colors ${!isLightMode ? 'bg-zinc-900' : 'bg-zinc-300'}`}>
                            <span className={`text-[8px] font-black ${!isLightMode ? 'text-red-500/80' : 'text-zinc-500/50'}`}>OFF</span>
                        </div>
                        
                        {/* Relief (Le bouton qui bascule) */}
                        <div 
                            className={`absolute top-0 bottom-0 w-[55%] transition-transform duration-200 ease-in-out border-l border-r border-black/10 ${
                                isLightMode 
                                ? 'translate-x-0 bg-gradient-to-r from-white to-zinc-200 shadow-[2px_0_3px_rgba(0,0,0,0.2)]' 
                                : 'translate-x-[82%] bg-gradient-to-r from-zinc-600 to-zinc-800 shadow-[-2px_0_3px_rgba(0,0,0,0.4)]'
                            }`} 
                        />
                    </button>

                    <button className="relative p-2 text-zinc-400 hover:text-zinc-100 transition-colors">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-purple-500 rounded-full"></span>
                    </button>

                    <div className="avatar">
                        <div className="w-8 h-8 rounded-full ring ring-cyan-500/30 ring-offset-base-100 ring-offset-2 bg-zinc-800 flex items-center justify-center cursor-pointer">
                            <User className="w-4 h-4 text-zinc-400" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
