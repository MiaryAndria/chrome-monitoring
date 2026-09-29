import { Download, FileText, FileSpreadsheet, X } from 'lucide-react';

function ExportModal({
    open,
    onClose,
    title = 'Exporter le rapport',
    subtitle = 'Choisissez le format de fichier',
    onExportPdf,
    onExportExcel,
}) {
    if (!open) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="modal-header-left">
                        <div className="modal-icon">
                            <Download className="w-5 h-5" />
                        </div>
                        <div>
                            <div className="modal-title">{title}</div>
                            <div className="modal-subtitle">{subtitle}</div>
                        </div>
                    </div>

                    <button
                        type="button"
                        className="modal-close-btn"
                        onClick={onClose}
                        aria-label="Fermer la fenêtre d'export"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                <div className="p-5 space-y-3">
                    <button
                        type="button"
                        onClick={onExportPdf}
                        className="w-full flex items-center justify-between gap-3 rounded-2xl border border-cyan-500/40 bg-gradient-to-r from-cyan-500/12 via-cyan-500/6 to-transparent px-4 py-3.5 text-left text-sm font-semibold text-cyan-200 shadow-[0_0_18px_rgba(34,211,238,0.08)] transition hover:border-cyan-400/60 hover:bg-cyan-500/15"
                    >
                        <span className="flex items-center gap-3">
                            <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl border border-cyan-500/40 bg-cyan-500/10 text-cyan-300">
                                <FileText className="w-4 h-4" />
                            </span>
                            Exporter en PDF
                        </span>
                        <span className="text-[10px] uppercase tracking-[0.2em] text-cyan-100/80">PDF</span>
                    </button>

                    <button
                        type="button"
                        onClick={onExportExcel}
                        className="w-full flex items-center justify-between gap-3 rounded-2xl border border-emerald-500/40 bg-gradient-to-r from-emerald-500/12 via-emerald-500/6 to-transparent px-4 py-3.5 text-left text-sm font-semibold text-emerald-200 shadow-[0_0_18px_rgba(16,185,129,0.08)] transition hover:border-emerald-400/60 hover:bg-emerald-500/15"
                    >
                        <span className="flex items-center gap-3">
                            <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-emerald-300">
                                <FileSpreadsheet className="w-4 h-4" />
                            </span>
                            Exporter en Excel
                        </span>
                        <span className="text-[10px] uppercase tracking-[0.2em] text-emerald-100/80">XLSX</span>
                    </button>
                </div>

                <div className="modal-footer">
                    <button type="button" className="modal-close-action-btn" onClick={onClose}>
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ExportModal;
