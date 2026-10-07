import React from 'react';

export default function GenericTable({ columns, data }) {
    return (
        <div className="overflow-x-auto w-full glass-panel border border-white/10 rounded-xl">
            <table className="w-full text-left text-sm text-zinc-300 whitespace-nowrap">
                <thead className="text-[10px] uppercase bg-white/5 text-zinc-400 border-b border-white/10 tracking-wider font-semibold">
                    <tr>
                        {columns.map((col, idx) => (
                            <th key={idx} className={`px-5 py-4 ${col.className || ''}`}>
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                    {data.length === 0 ? (
                        <tr>
                            <td colSpan={columns.length} className="px-6 py-8 text-center text-zinc-500">
                                Aucune donnée disponible
                            </td>
                        </tr>
                    ) : (
                        data.map((row, rowIndex) => (
                            <tr key={rowIndex} className="hover:bg-white/5 transition-colors group">
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
                                        <td key={colIndex} className={`px-5 py-3 ${col.className || ''}`}>
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
