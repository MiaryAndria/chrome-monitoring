import api_service from '../../api/api_service';

export const formatBytes = (bytes) => {
    if (!bytes && bytes !== 0) return 'N/A';
    const num = typeof bytes === 'string' ? parseInt(bytes) : bytes;
    if (isNaN(num) || num === 0) return '0 B';
    const sizes = ['B', 'Ko', 'Mo', 'Go', 'To'];
    const i = Math.floor(Math.log(num) / Math.log(1024));
    return `${(num / Math.pow(1024, i)).toFixed(i > 2 ? 2 : 0)} ${sizes[i]}`;
};

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

export const usagePercent = (free, total) => {
    const f = parseInt(free), t = parseInt(total);
    if (isNaN(f) || isNaN(t) || t === 0) return null;
    return Math.round(((t - f) / t) * 100);
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

const showExportSuccess = (message) => {
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

    const badge = document.createElement('span');
    badge.textContent = fileType;
    badge.style.display = 'inline-block';
    badge.style.marginLeft = '8px';
    badge.style.padding = '4px 8px';
    badge.style.borderRadius = '999px';
    badge.style.background = '#22c55e';
    badge.style.color = '#fff';
    badge.style.fontSize = '11px';
    badge.style.fontWeight = '700';

    toast.appendChild(badge);

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3500);
};

export const exportPdf = async ({ onglet, id, date_debut, date_fin } = {}) => {
    if (!onglet || !id) {
        throw new Error('Les paramètres onglet et id sont requis pour exporter en PDF.');
    }

    const params = new URLSearchParams();
    if (date_debut) params.set('date_debut', date_debut);
    if (date_fin) params.set('date_fin', date_fin);

    const query = params.toString() ? `?${params.toString()}` : '';
    const response = await api_service.get(`/rapport/export/pdf/${encodeURIComponent(onglet)}/${id}${query}`);

    const fileUrl = response.data?.url || response.data?.file_url;

    if (fileUrl) {
        window.open(fileUrl, '_blank', 'noopener,noreferrer');
    }

    showExportSuccess('Rapport PDF généré dans export/pdf');
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
    const response = await api_service.get(`/rapport/export/excel/${encodeURIComponent(onglet)}/${id}${query}`);

    const fileUrl = response.data?.url || response.data?.file_url;

    if (fileUrl) {
        window.open(fileUrl, '_blank', 'noopener,noreferrer');
    }

    showExportSuccess('Rapport Excel généré dans export/excel');
    return response;
};