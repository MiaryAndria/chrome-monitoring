import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { GetMe } from '../fonction/userFonction';

export default function PublicRoute() {
    const [checking, setChecking] = useState(true);
    const [authenticated, setAuthenticated] = useState(false);

    useEffect(() => {
        let actif = true;

        const verifier = async () => {
            try {
                await GetMe();
                if (actif) setAuthenticated(true);
            } catch (e) {
                if (actif) setAuthenticated(false);
            } finally {
                if (actif) setChecking(false);
            }
        };

        verifier();

        return () => {
            actif = false;
        };
    }, []);

    if (checking) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-[#050508] text-sm text-zinc-400">
                Chargement…
            </div>
        );
    }

    if (authenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    return <Outlet />;
}
