import { useEffect, useState } from 'react';
import Skeleton from '../../components/Skeleton';
import { getDureeVieEvenement } from '../../fonction/eventFonction';
import { formatDateTime, formatDuration } from '../../fonction/utils/util';

function EvenementDureeVie({ eventId }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!eventId) return;
        let annule = false;

        setLoading(true);
        getDureeVieEvenement(eventId)
            .then((resultat) => {
                if (!annule) setData(resultat);
            })
            .finally(() => {
                if (!annule) setLoading(false);
            });

        return () => {
            annule = true;
        };
    }, [eventId]);

    if (loading) {
        return <Skeleton className="h-20 w-full" />;
    }

    if (!data) {
        return <p className="text-[11px] text-zinc-500 italic">Durée de vie indisponible.</p>;
    }

    const batterie = data.details?.batterie;
    const minutes = data.duree_vie;

    const autonomie = minutes !== null && minutes !== undefined
        ? `${Math.floor(minutes / 60)} h ${Math.round(minutes % 60)} min`
        : (batterie?.etat === 'Charging' ? 'En charge' : 'Non estimable');

    const etat = batterie?.etat === 'Charging'
        ? 'En charge'
        : batterie?.etat === 'Discharging' ? 'Sur batterie' : 'Inconnu';

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
            <div className="bg-zinc-900/60 rounded-lg p-3 border border-white/5">
                <p className="text-[10px] uppercase text-zinc-500 mb-1">Autonomie estimée</p>
                <p className="font-semibold text-emerald-300">{autonomie}</p>
                {batterie && (
                    <p className="text-zinc-400 mt-1">
                        {etat} · {batterie.charge_rate ?? '—'} % · {batterie.cycle_count ?? '—'} cycle(s)
                    </p>
                )}
            </div>
            <div className="bg-zinc-900/60 rounded-lg p-3 border border-white/5">
                <p className="text-[10px] uppercase text-zinc-500 mb-1">Dernier événement</p>
                <p className="font-semibold text-cyan-300">
                    {formatDuration(data.details?.secondes_depuis_dernier_evenement)}
                </p>
                <p className="text-zinc-400 mt-1">
                    {formatDateTime(data.details?.dernier_evenement)}
                </p>
            </div>
        </div>
    );
}

export default EvenementDureeVie;
