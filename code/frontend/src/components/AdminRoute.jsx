import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { GetMe } from '../fonction/userFonction';

export const ID_ROLE_ADMIN = 1;

export default function AdminRoute() {
    const [checking, setChecking] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        let actif = true;
        GetMe()
            .then((u) => { if (actif) setIsAdmin(u?.id_role === ID_ROLE_ADMIN); })
            .catch(() => { if (actif) setIsAdmin(false); })
            .finally(() => { if (actif) setChecking(false); });
        return () => { actif = false; };
    }, []);

    if (checking) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-[#050508] text-sm text-zinc-400">
                Chargement…
            </div>
        );
    }

    if (!isAdmin) {
        return <Navigate to="/dashboard" replace />;
    }

    return <Outlet />;
}
