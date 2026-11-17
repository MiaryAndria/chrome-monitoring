import { useEffect, useState } from 'react';
import { KeyRound, Eye, EyeOff, Save } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import { GetMe, updateUserPassword } from '../../fonction/userFonction';
import '../../css/liste.css';

function UpdatePassword() {
    const [me, setMe] = useState(null);
    const [ancien, setAncien] = useState('');
    const [nouveau, setNouveau] = useState('');
    const [confirmation, setConfirmation] = useState('');
    const [showAncien, setShowAncien] = useState(false);
    const [showNouveau, setShowNouveau] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const charger = async () => {
            try {
                const data = await GetMe();
                setMe(data);
            } catch (e) {
                setError("Impossible de récupérer les informations de l'utilisateur.");
            }
        };
        charger();
    }, []);

    const onSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        try {
            setLoading(true);
            await updateUserPassword(me?.id, ancien, nouveau, confirmation);
            setSuccess('Mot de passe mis à jour avec succès.');
            setAncien('');
            setNouveau('');
            setConfirmation('');
        } catch (e) {
            setError(e.response?.data?.error || e.response?.data?.detail || 'Erreur lors de la mise à jour du mot de passe.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <PageLayout
            title="Mot de passe"
            subtitle="Mettre à jour le mot de passe de votre compte"
            titleIcon={KeyRound}
        >
            <div className="glass-panel rounded-2xl p-6 max-w-xl">
                <form onSubmit={onSubmit} className="space-y-5">
                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Ancien mot de passe</label>
                        <div className="relative">
                            <input
                                type={showAncien ? 'text' : 'password'}
                                value={ancien}
                                onChange={(e) => setAncien(e.target.value)}
                                placeholder="Saisissez votre mot de passe actuel"
                                className="w-full px-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 pr-10"
                                autoComplete="current-password"
                            />
                            <button
                                type="button"
                                onClick={() => setShowAncien((v) => !v)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-cyan-400 cursor-pointer"
                                aria-label={showAncien ? 'Masquer' : 'Afficher'}
                            >
                                {showAncien ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Nouveau mot de passe</label>
                        <div className="relative">
                            <input
                                type={showNouveau ? 'text' : 'password'}
                                value={nouveau}
                                onChange={(e) => setNouveau(e.target.value)}
                                placeholder="Saisissez un nouveau mot de passe (6 caractères min.)"
                                className="w-full px-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50 pr-10"
                                autoComplete="new-password"
                            />
                            <button
                                type="button"
                                onClick={() => setShowNouveau((v) => !v)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-cyan-400 cursor-pointer"
                                aria-label={showNouveau ? 'Masquer' : 'Afficher'}
                            >
                                {showNouveau ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-zinc-400 mb-1.5">Confirmer le nouveau mot de passe</label>
                        <input
                            type="password"
                            value={confirmation}
                            onChange={(e) => setConfirmation(e.target.value)}
                            placeholder="Confirmez le nouveau mot de passe"
                            className="w-full px-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50"
                            autoComplete="new-password"
                        />
                    </div>

                    {error && (
                        <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                            {error}
                        </div>
                    )}
                    {success && (
                        <div className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 p-2.5 rounded-lg">
                            {success}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25 disabled:opacity-50 transition-colors cursor-pointer text-sm font-semibold"
                    >
                        <Save className="w-4 h-4" />
                        {loading ? 'Mise à jour…' : 'Mettre à jour'}
                    </button>
                </form>
            </div>
        </PageLayout>
    );
}

export default UpdatePassword;
