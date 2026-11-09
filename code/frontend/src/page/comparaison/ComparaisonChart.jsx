import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
} from "recharts";

function ComparaisonChart({ resultat, labels }) {
    if (!resultat) return null;

    const cpuA = resultat.cpu?.usage?.a?.moyenne ?? null;
    const cpuB = resultat.cpu?.usage?.b?.moyenne ?? null;
    const ramA = resultat.ram?.usage?.a?.moyenne_pct ?? null;
    const ramB = resultat.ram?.usage?.b?.moyenne_pct ?? null;

    const aucuneDonnee = cpuA == null && cpuB == null && ramA == null && ramB == null;
    if (aucuneDonnee) {
        return (
            <div className="glass-panel rounded-2xl p-5 text-sm text-zinc-500">
                Aucune donnée à tracer.
            </div>
        );
    }

    const data = [
        { metrique: "CPU", A: cpuA, B: cpuB },
        { metrique: "RAM", A: ramA, B: ramB },
    ];

    const formatPct = (v) => (v == null ? "—" : `${v} %`);

    return (
        <div className="glass-panel rounded-2xl p-5">
            <div className="flex items-center justify-between gap-3 mb-3">
                <h3 className="text-sm font-semibold text-zinc-200">Usage moyen comparé</h3>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-zinc-400 justify-end">
                    <span className="flex items-center gap-1.5 min-w-0">
                        <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: "#06b6d4" }} />
                        <span className="truncate max-w-[220px]">A : {labels.a}</span>
                    </span>
                    <span className="flex items-center gap-1.5 min-w-0">
                        <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ background: "#a855f7" }} />
                        <span className="truncate max-w-[220px]">B : {labels.b}</span>
                    </span>
                </div>
            </div>

            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={data}
                        margin={{ top: 10, right: 10, left: -20, bottom: 4 }}
                        barGap={6}
                        barCategoryGap="40%"
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis
                            dataKey="metrique"
                            stroke="#71717a"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis
                            stroke="#71717a"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(v) => `${v}%`}
                            domain={[0, 100]}
                            ticks={[0, 20, 40, 60, 80, 100]}
                        />
                        <RechartsTooltip
                            contentStyle={{
                                backgroundColor: "rgba(24, 24, 32, 0.9)",
                                border: "1px solid rgba(255,255,255,0.1)",
                                borderRadius: "8px",
                            }}
                            cursor={{ fill: "rgba(255,255,255,0.05)" }}
                            formatter={(val, name) => [formatPct(val), name === "A" ? labels.a : labels.b]}
                        />

                        <Bar
                            dataKey="A"
                            name="A"
                            fill="#06b6d4"
                            barSize={18}
                            radius={[4, 4, 0, 0]}
                            activeBar={{ fill: "#67e8f9", stroke: "#a5f3fc", strokeWidth: 1 }}
                        />
                        <Bar
                            dataKey="B"
                            name="B"
                            fill="#a855f7"
                            barSize={18}
                            radius={[4, 4, 0, 0]}
                            activeBar={{ fill: "#c084fc", stroke: "#e9d5ff", strokeWidth: 1 }}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export default ComparaisonChart;
