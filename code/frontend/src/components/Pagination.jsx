import { memo } from 'react';

function Pagination({ page, pageSize, totalPages, total, loading, onPageChange, onPageSizeChange }) {
    const pages = totalPages || 1;
    const totalLabel = total > 1 ? `${total} résultats` : `${total} résultat`;

    return (
        <div className="flex flex-wrap justify-center items-center gap-4 mt-8 pb-4">
            <label className="flex items-center gap-2 text-xs text-zinc-400">
                Par page
                <select
                    value={pageSize}
                    onChange={(e) => onPageSizeChange(Number(e.target.value))}
                    className="bg-zinc-900 border border-white/10 rounded-lg px-2 py-1 text-xs text-zinc-300 outline-none focus:border-cyan-500/50"
                >
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                </select>
            </label>

            <button
                className="pagination-btn"
                disabled={loading || page <= 1}
                onClick={() => onPageChange(page - 1)}
            >
                Précédent
            </button>

            <div className="pagination-indicator">
                {page} <span className="pagination-separator">/</span> {pages}
            </div>

            <button
                className="pagination-btn"
                disabled={loading || page >= pages}
                onClick={() => onPageChange(page + 1)}
            >
                Suivant
            </button>

            <span className="text-xs text-zinc-500">{totalLabel}</span>
        </div>
    );
}

export default memo(Pagination);
