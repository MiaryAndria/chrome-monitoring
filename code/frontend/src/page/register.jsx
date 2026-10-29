import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { User, Mail, KeyRound, ShieldCheck, UserPlus } from 'lucide-react';
import MouseSpotlight from "../components/MouseSpotlight";
import { Register } from "../fonction/userFonction";
import '../css/login.css';

function Inscription() {
    const [nom, setNom] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const register = async (e) => {
        e.preventDefault();
        if (loading) return;
        setError('');

        if (!nom.trim() || !email.trim() || !password) {
            setError('Tous les champs sont obligatoires.');
            return;
        }
        if (password.length < 6) {
            setError('Le mot de passe doit contenir au moins 6 caractères.');
            return;
        }
        if (password !== confirm) {
            setError('Les mots de passe ne correspondent pas.');
            return;
        }

        try {
            setLoading(true);
            await Register(nom, email, password);
            navigate('/dashboard', { replace: true, state: { welcome: true } });
        } catch (err) {
            setError(err.response?.data?.detail || "Impossible de créer le compte.");
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
                        <UserPlus className="w-8 h-8 text-cyan-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-wider text-zinc-100">Créer un compte</h1>
                    <p className="text-xs text-zinc-400 mt-1 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Accès lecture seule par défaut
                    </p>
                </div>

                <form onSubmit={register} className="space-y-5">
                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Nom</label>
                        <div className="relative flex items-center">
                            <User className="w-4 h-4 absolute left-3.5 text-zinc-500 z-10 pointer-events-none" />
                            <input
                                type="text"
                                className="login-input"
                                value={nom}
                                onChange={(e) => { setNom(e.target.value); setError(''); }}
                                placeholder="Nom complet"
                                autoComplete="name"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Email</label>
                        <div className="relative flex items-center">
                            <Mail className="w-4 h-4 absolute left-3.5 text-zinc-500 z-10 pointer-events-none" />
                            <input
                                type="email"
                                className="login-input"
                                value={email}
                                onChange={(e) => { setEmail(e.target.value); setError(''); }}
                                placeholder="utilisateur@gmail.com"
                                autoComplete="email"
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
                                onChange={(e) => { setPassword(e.target.value); setError(''); }}
                                placeholder="••••••••"
                                autoComplete="new-password"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Confirmer le mot de passe</label>
                        <div className="relative flex items-center">
                            <KeyRound className="w-4 h-4 absolute left-3.5 text-zinc-500 z-10 pointer-events-none" />
                            <input
                                type="password"
                                className="login-input"
                                value={confirm}
                                onChange={(e) => { setConfirm(e.target.value); setError(''); }}
                                placeholder="••••••••"
                                autoComplete="new-password"
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg text-center">
                            {error}
                        </div>
                    )}

                    <button type="submit" className="login-button mt-3" disabled={loading}>
                        {loading ? 'Création en cours…' : "S'inscrire"}
                    </button>
                </form>

                <p className="text-xs text-zinc-400 text-center mt-6">
                    Déjà un compte ?{' '}
                    <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-medium">
                        Se connecter
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Inscription;
