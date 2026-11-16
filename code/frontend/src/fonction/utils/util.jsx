import api_service from '../../api/api_service';

export const formatBytes = (bytes) => {
    if (!bytes && bytes !== 0) return 'N/A';
    const num = typeof bytes === 'string' ? parseInt(bytes) : bytes;
    if (isNaN(num) || num === 0) return '0 B';
    const sizes = ['B', 'Ko', 'Mo', 'Go', 'To'];
    const i = Math.floor(Math.log(num) / Math.log(1000));
    return `${(num / Math.pow(1000, i)).toFixed(i > 2 ? 2 : 0)} ${sizes[i]}`;
};

// export const formatBytes = (bytes) => {
//     if (!bytes && bytes !== 0) return 'N/A';
//     const num = typeof bytes === 'string' ? parseInt(bytes) : bytes;
//     if (isNaN(num) || num === 0) return '0 B';
//     const sizes = ['B', 'Ko', 'Mo', 'Go', 'To'];
//     const i = Math.floor(Math.log(num) / Math.log(1024));
//     return `${(num / Math.pow(1024, i)).toFixed(i > 2 ? 2 : 0)} ${sizes[i]}`;
// };

export const cleanLabel = (label) => {
    if (!label) return 'Inconnu';
    return label.replace(/\n/g, '').trim();
};

export const getTempStyle = (temp) => {
    if (temp < 40) return { text: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', bar: 'bg-emerald-500' };
    if (temp < 55) return { text: 'text-cyan-400', bg: 'bg-cyan-500/15', border: 'border-cyan-500/30', bar: 'bg-cyan-500' };
    if (temp < 70) return { text: 'text-amber-400', bg: 'bg-amber-500/15', border: 'border-amber-500/30', bar: 'bg-amber-500' };
    return { text: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500/30', bar: 'bg-red-500' };
};

export const formatDate = (dateStr) => {
    if (!dateStr) return null;
    try {
        return new Date(dateStr).toLocaleString('fr-FR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch { return dateStr; }
};

const ADMIN_TIMEZONE = import.meta.env.VITE_ADMIN_TIMEZONE || 'Indian/Antananarivo';

export const formatDateTime = (dateStr) => {
    if (!dateStr) return '—';
    try {
        return new Intl.DateTimeFormat('fr-FR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: false,
            timeZone: ADMIN_TIMEZONE
        }).format(new Date(dateStr));
    } catch {
        return dateStr;
    }
};

export const usagePercent = (free, total) => {
    const f = parseInt(free), t = parseInt(total);
    if (isNaN(f) || isNaN(t) || t === 0) return null;
    return Math.round(((t - f) / t) * 100);   // (total - libre) / total * 100
};

export const formatDuration = (seconds) => {
    if (seconds === null || seconds === undefined) return '—';

    const total = Math.max(0, Math.floor(seconds));
    const jours = Math.floor(total / 86400);
    const heures = Math.floor((total % 86400) / 3600);
    const minutes = Math.floor((total % 3600) / 60);

    if (jours > 0) return `${jours} j ${heures} h`;
    if (heures > 0) return `${heures} h ${minutes} min`;
    return `${minutes} min`;
};

export const getUtilColor = (pct) => {
    if (pct < 30) return 'text-emerald-400';
    if (pct < 60) return 'text-cyan-400';
    if (pct < 85) return 'text-amber-400';
    return 'text-red-400';
};

export const getUtilBarColor = (pct) => {
    if (pct < 30) return 'bg-emerald-500';
    if (pct < 60) return 'bg-cyan-500';
    if (pct < 85) return 'bg-amber-500';
    return 'bg-red-500';
};

const showExportSuccess = (message, fileType) => {
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.right = '20px';
    toast.style.bottom = '20px';
    toast.style.zIndex = '99999';
    toast.style.background = 'rgba(17, 24, 39, 0.95)';
    toast.style.color = '#fff';
    toast.style.borderRadius = '12px';
    toast.style.padding = '14px 18px';
    toast.style.boxShadow = '0 12px 30px rgba(0,0,0,0.22)';
    toast.style.fontSize = '14px';
    toast.style.fontWeight = '600';
    toast.style.maxWidth = '320px';
    toast.style.border = '1px solid rgba(255,255,255,0.08)';
    toast.textContent = message;

    if (fileType) {
        const badge = document.createElement('span');
        badge.textContent = fileType;
        badge.style.display = 'inline-block';
        badge.style.marginLeft = '8px';
        badge.style.padding = '4px 8px';
        badge.style.borderRadius = '999px';
        badge.style.background = fileType === 'PDF' ? '#ef4444' : '#22c55e'; // Red for PDF, Green for Excel
        badge.style.color = '#fff';
        badge.style.fontSize = '11px';
        badge.style.fontWeight = '700';
        toast.appendChild(badge);
    }

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease-out';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
};

export const exportPdf = async ({ onglet, id, date_debut, date_fin } = {}) => {
    if (!onglet || !id) {
        throw new Error('Les paramètres onglet et id sont requis pour exporter en PDF.');
    }

    const params = new URLSearchParams();
    if (date_debut) params.set('date_debut', date_debut);
    if (date_fin) params.set('date_fin', date_fin);

    const query = params.toString() ? `?${params.toString()}` : '';
    const url = `/rapport/export/pdf/${encodeURIComponent(onglet)}/${id}${query}`;
    const response = await api_service.get(url, { responseType: 'blob' });

    const disposition = response.headers['content-disposition'] || '';
    const match = disposition.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : 'rapport.xlsx';

    const objectUrl = window.URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(objectUrl);

    showExportSuccess('Rapport généré avec succès', 'PDF');
    return response;
};

export const exportExcel = async ({ onglet, id, date_debut, date_fin } = {}) => {
    if (!onglet || !id) {
        throw new Error('Les paramètres onglet et id sont requis pour exporter en Excel.');
    }

    const params = new URLSearchParams();
    if (date_debut) params.set('date_debut', date_debut);
    if (date_fin) params.set('date_fin', date_fin);

    const query = params.toString() ? `?${params.toString()}` : '';
    const url = `/rapport/export/excel/${encodeURIComponent(onglet)}/${id}${query}`;
    const response = await api_service.get(url, { responseType: 'blob' });

    const disposition = response.headers['content-disposition'] || '';
    const match = disposition.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : 'rapport.xlsx';

    const objectUrl = window.URL.createObjectURL(new Blob([response.data]));
    const a = document.createElement('a');
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(objectUrl);

    showExportSuccess('Rapport généré avec succès', 'Excel');
    return response;
};

export const formatFreq = (khz) => {
    const n = Number(khz);
    if (!n) return "—";
    return `${(n / 1_000_000).toFixed(1)} GHz`;
}

export const Badge = ({ gagnant, labels }) => {
    if (gagnant === "indetermine") {
        return (
            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-zinc-500/10 text-zinc-400 border border-white/10">
                Indéterminé
            </span>
        );
    }
    if (gagnant === "egal") {
        return (
            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-zinc-500/10 text-zinc-300 border border-white/10">
                Égalité
            </span>
        );
    }
    return (
        <span className="text-[11px] px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
            {gagnant === "a" ? labels.a : labels.b} en tête
        </span>
    );
}

export const Bloc = ({ titre, gagnant, labels, ligneA, ligneB, ecart }) => {
    return (
        <div className="rounded-xl border border-white/10 p-4 bg-zinc-900/40 space-y-3">
            <div className="flex items-center justify-between gap-2">
                <span className="text-xs uppercase tracking-wider text-zinc-400 font-semibold">{titre}</span>
                <Badge gagnant={gagnant} labels={labels} />
            </div>
            <div className="grid grid-cols-2 gap-3">
                <div className="space-y-0.5 min-w-0">
                    <div className="text-[11px] text-zinc-500 truncate">{labels.a}</div>
                    {ligneA.map((l, i) => (
                        <div key={i} className="text-sm text-zinc-200 break-words">{l}</div>
                    ))}
                </div>
                <div className="space-y-0.5 min-w-0">
                    <div className="text-[11px] text-zinc-500 truncate">{labels.b}</div>
                    {ligneB.map((l, i) => (
                        <div key={i} className="text-sm text-zinc-200 break-words">{l}</div>
                    ))}
                </div>
            </div>
            {ecart != null && <div className="text-[11px] text-zinc-500">Écart : {ecart}</div>}
        </div>
    );
}

export const colorMap = {
    cyan: { icon: 'bg-cyan-500/10 text-cyan-400', border: 'hover:border-cyan-500/30', val: 'text-cyan-400' },
    purple: { icon: 'bg-purple-500/10 text-purple-400', border: 'hover:border-purple-500/30', val: 'text-purple-400' },
    amber: { icon: 'bg-amber-500/10 text-amber-400', border: 'hover:border-amber-500/30', val: 'text-amber-400' },
    emerald: { icon: 'bg-emerald-500/10 text-emerald-400', border: 'hover:border-emerald-500/30', val: 'text-emerald-400' },
    blue: { icon: 'bg-blue-500/10 text-blue-400', border: 'hover:border-blue-500/30', val: 'text-blue-400' },
    pink: { icon: 'bg-pink-500/10 text-pink-400', border: 'hover:border-pink-500/30', val: 'text-pink-400' },
};

export const CarteRessource = ({ titre, children }) => {
    return (
        <div className="glass-panel rounded-2xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-zinc-200">{titre}</h3>
            {children}
        </div>
    );
}

export const formatPct = (value) => {
    return value == null ? "—" : `${value} %`;
}

export const ligneUsageCpu = (c) => {
    if (!c || c.moyenne == null) return ["Aucune donnée relevée"];
    return [`${formatPct(c.moyenne)} (moyenne)`, `min ${formatPct(c.min)} · max ${formatPct(c.max)} · n ${c.n}`];
}

export const ligneUsageRam = (r) => {
    if (!r || r.moyenne_pct == null) return ["Aucune donnée relevée"];
    return [`${formatPct(r.moyenne_pct)} utilisés`, `${formatBytes(r.moyenne_util) || "—"} / ${formatBytes(r.total) || "—"}`];
}

export const lignePuissanceCpu = (s) => {
    return [s.cpu_model || "—", `${formatFreq(s.freq_max_proc)} · ${s.cpu_architecture || "—"}`, `score ${s.score ?? "—"}`];
}

export const lignePuissanceRam = (s) => {
    return [formatBytes(s.ram_total) || "—", `score ${s.score ?? "—"}`];
}
