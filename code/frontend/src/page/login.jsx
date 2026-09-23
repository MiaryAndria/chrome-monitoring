import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Activity, User, KeyRound, ShieldCheck } from 'lucide-react';
import MouseSpotlight from "../components/MouseSpotlight";
import { Login } from "../fonction/userFonction";
import '../css/login.css';

function Connexion() {
    const [password, setPassword] = useState('');
    const [nom, setNom] = useState('');
    const [error, setError] = useState(false);

    const navigate = useNavigate();

    const login = async (e) => {
        e.preventDefault(); // Empêcher le rechargement de la page
        try {
            await Login(nom, password);
            navigate('/filiale');
        } catch(e) {
            console.log(e);
            setError(true);
        }
    }

    return (
        <div className="login-container" data-theme="dark">
            <div className="cyber-grid"></div>
            <MouseSpotlight />
            <div className="animated-neon-wrapper">
                <div className="login-card">
                    <div className="flex flex-col items-center mb-8">
                        <div className="relative p-3 bg-cyan-500/10 rounded-2xl border border-cyan-500/30 mb-3 group cursor-pointer">
                            <Activity className="w-8 h-8 text-cyan-400 animate-pulse" />
                            <div className="absolute inset-0 bg-cyan-400/20 rounded-2xl blur-md -z-10 group-hover:bg-cyan-400/40 transition-all"></div>
                        </div>
                        <h1 className="text-2xl font-bold tracking-wider text-zinc-100 flex items-center gap-2">
                            GT
                        </h1>
                        <p className="text-xs text-zinc-400 mt-1 flex items-center gap-1">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> System Access & Security
                        </p>
                    </div>

                    <form onSubmit={login} className="space-y-5">
                        <div>
                            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Identifiant</label>
                            <div className="relative flex items-center">
                                <User className="w-4 h-4 absolute left-3.5 text-cyan-400 z-10 pointer-events-none" />
                                <input
                                    type="text"
                                    className="login-input"
                                    value={nom}
                                    onChange={(e) => { setNom(e.target.value); setError(false); }}
                                    placeholder="Nom d'utilisateur"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-zinc-400 mb-1.5">Mot de passe</label>
                            <div className="relative flex items-center">
                                <KeyRound className="w-4 h-4 absolute left-3.5 text-cyan-400 z-10 pointer-events-none" />
                                <input
                                    type="password"
                                    className="login-input"
                                    value={password}
                                    onChange={(e) => { setPassword(e.target.value); setError(false); }}
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg text-center animate-bounce">
                                Identifiant ou mot de passe incorrect.
                            </div>
                        )}

                        <button type="submit" className="login-button mt-3">
                            Se connecter
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Connexion;
