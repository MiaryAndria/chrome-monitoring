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
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const login = async (e) => {
        e.preventDefault();
        if (loading) return;
        try {
            setLoading(true);
            await Login(nom, password);
            navigate('/dashboard', { replace: true });
        } catch (e) {
            console.log(e);
            setError(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container" data-theme="dark">
            <div className="cyber-grid"></div>
            <MouseSpotlight />

            <div className="login-card">
                <div className="flex flex-col items-center mb-8">
                    <div className="p-3 bg-cyan-500/10 rounded-2xl border border-cyan-500/30 mb-3">
                        <Activity className="w-8 h-8 text-cyan-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-wider text-zinc-100">GT</h1>
                    <p className="text-xs text-zinc-400 mt-1 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> System Access & Security
                    </p>
                </div>

                <form onSubmit={login} className="space-y-5">
                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Identifiant</label>
                        <div className="relative flex items-center">
                            <User className="w-4 h-4 absolute left-3.5 text-zinc-500 z-10 pointer-events-none" />
                            <input
                                type="text"
                                className="login-input"
                                value={nom}
                                onChange={(e) => { setNom(e.target.value); setError(false); }}
                                placeholder="utilisateur@gmail.com"
                                autoComplete="username"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Mot de passe</label>
                        <div className="relative flex items-center">
                            <KeyRound className="w-4 h-4 absolute left-3.5 text-zinc-500 z-10 pointer-events-none" />
                            <input
                                type="password"
                                className="login-input"
                                value={password}
                                onChange={(e) => { setPassword(e.target.value); setError(false); }}
                                placeholder="••••••••"
                                autoComplete="current-password"
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg text-center">
                            Identifiant ou mot de passe incorrect.
                        </div>
                    )}

                    <button type="submit" className="login-button mt-3" disabled={loading}>
                        {loading ? 'Connexion en cours…' : 'Se connecter'}
                    </button>
                </form>

                <p className="text-xs text-zinc-400 text-center mt-6">
                    Pas encore de compte ?{' '}
                    <button
                        type="button"
                        onClick={() => navigate('/register')}
                        className="text-cyan-400 hover:text-cyan-300 font-medium cursor-pointer"
                    >
                        Créer un compte
                    </button>
                </p>
            </div>
        </div>
    );
}

export default Connexion;
