import React from 'react';

export default function GenericTable({ columns, data, onRowClick }) {
    const rows = Array.isArray(data) ? data : [];
    return (
        <div className="overflow-x-auto w-full glass-panel border border-white/10 rounded-xl">
            <table className="w-full text-left text-sm text-zinc-300">
                <thead className="text-[10px] uppercase bg-white/5 text-zinc-400 border-b border-white/10 tracking-wider font-semibold">
                    <tr>
                        {columns.map((col, idx) => (
                            <th key={idx} className={`px-5 py-4 ${col.className || ''} ${col.sticky ? 'sticky right-0 z-20 bg-[#16161c] border-l border-white/10' : ''}`}>
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    {rows.length === 0 ? (
                        <tr>
                            <td colSpan={columns.length} className="px-6 py-10 text-center text-zinc-500">
                                <span className="block font-medium text-zinc-400">Aucune donnée à afficher</span>
                                <span className="block text-xs mt-1">Aucun résultat pour les critères actuels.</span>
                            </td>
                        </tr>
                    ) : (
                        rows.map((row, rowIndex) => (
                            <tr
                                key={rowIndex}
                                className={`hover:bg-white/5 transition-colors group ${onRowClick ? 'cursor-pointer' : ''}`}
                                onClick={onRowClick ? () => onRowClick(row) : undefined}
                            >
                                {columns.map((col, colIndex) => {
                                    let cellData;
                                    if (col.render) {
                                        cellData = col.render(row, rowIndex);
                                    } else if (typeof col.accessor === 'function') {
                                        cellData = col.accessor(row);
                                    } else {
                                        cellData = row[col.accessor];
                                    }
                                    return (
                                        <td key={colIndex} className={`px-5 py-3 align-top break-words ${col.className || ''} ${col.sticky ? 'sticky right-0 z-10 bg-[#0f0f14] group-hover:bg-[#1a1a21] border-l border-white/10' : ''}`}>
                                            {cellData}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
}
