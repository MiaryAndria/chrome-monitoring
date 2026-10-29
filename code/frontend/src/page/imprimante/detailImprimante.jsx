import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Printer, Monitor, Users, ArrowLeft, Download } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import GenericTable from "../../components/GenericTable";
import EmptyState from "../../components/EmptyState";
import Skeleton from "../../components/Skeleton";
import TableSkeleton from "../../components/skeletons/TableSkeleton";
import { getImprimanteDetail } from "../../fonction/imprimanteFonction";
import { formatDate, exportPdf, exportExcel } from "../../fonction/utils/util";
import '../../css/liste.css';
import ExportModal from '../../components/ExportModal';

function DetailImprimante() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [imprimante, setImprimante] = useState(null);
    const [loading, setLoading] = useState(true);
    const [modal, setModal] = useState(false);
    const [error, setError] = useState(null);
    const handleExport = async (format) => {
        try {
            const exportFn = format === 'pdf' ? exportPdf : exportExcel;
            await exportFn({ onglet: 'imprimante', id: id });
        } catch (e) {
            console.error(e);
        }
    };
    useEffect(() => {
        const charger = async () => {
            try {
                setLoading(true);
                setError(null);
                const result = await getImprimanteDetail(id);
                setImprimante(result);
            } catch (e) {
                console.error(e);
                setError("Impossible de charger le détail de l'imprimante.");
            } finally {
                setLoading(false);
            }
        };
        charger();
    }, [id]);

    const deviceColumns = [
        { header: "Modèle", render: (d) => <span className="font-bold text-zinc-100">{d.modele || "-"}</span> },
        { header: "N° de série", render: (d) => <span className="font-mono text-zinc-400">{d.serial_number || "-"}</span> },
        { header: "IP", render: (d) => <span className="font-mono text-zinc-400">{d.ip_adress || "-"}</span> },
        { header: "MAC", render: (d) => <span className="font-mono text-zinc-400">{d.mac_adress || "-"}</span> },
        { header: "ChromeOS", render: (d) => d.chromeos_version || "-" },
        { header: "Dernière détection", render: (d) => formatDate(d.derniere_detection) },
    ];

    const userColumns = [
        { header: "Email", render: (u) => <span className="font-bold text-zinc-100">{u.email}</span> },
        { header: "Dernière utilisation", render: (u) => formatDate(u.derniere_utilisation) },
    ];

    if (loading) {
        return (
            <PageLayout title="Détail imprimante" titleIcon={Printer}>
                <div className="space-y-6">
                    <Skeleton className="h-24 w-full" />
                    <TableSkeleton rows={4} />
                    <TableSkeleton rows={3} />
                </div>
            </PageLayout>
        );
    }

    if (error || !imprimante) {
        return (
            <PageLayout title="Détail imprimante" titleIcon={Printer}>
                <EmptyState icon={Printer} title={error || "Imprimante introuvable"} />
            </PageLayout>
        );
    }

    const devices = imprimante.device || [];
    const users = imprimante.user || [];

    return (
        <PageLayout
            title={imprimante.nom || "Imprimante"}
            subtitle={imprimante.vendor || "Fabricant inconnu"}
            titleIcon={Printer}
            contentClassName="space-y-8"
        >

            {/* Infos générales */}
            <div className="glass-panel rounded-2xl p-6 grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                    <p className="text-xs text-zinc-500 mb-1">Fabricant</p>
                    <p className="font-bold text-zinc-100">{imprimante.vendor || "-"}</p>
                </div>
                <div>
                    <p className="text-xs text-zinc-500 mb-1">Modèle / Nom</p>
                    <p className="font-bold text-zinc-100">{imprimante.nom || "-"}</p>
                </div>
                <div>
                    <p className="text-xs text-zinc-500 mb-1">VID</p>
                    <p className="font-mono text-zinc-300">{imprimante.vid ?? "-"}</p>
                </div>
                <div>
                    <p className="text-xs text-zinc-500 mb-1">PID</p>
                    <p className="font-mono text-zinc-300">{imprimante.pid ?? "-"}</p>
                </div>
            </div>

            {/* Devices */}
            <section className="space-y-4">
                <div className="section-header">
                    <h2 className="section-title flex items-center gap-2">
                        <Monitor className="w-5 h-5" /> Devices
                    </h2>
                    <span className="section-count">
                        {devices.length} device{devices.length > 1 ? "s" : ""}
                    </span>
                </div>
                {devices.length === 0 ? (
                    <EmptyState icon={Monitor} title="Aucun device associé" />
                ) : (
                    <GenericTable columns={deviceColumns} data={devices} />
                )}
            </section>

            {/* Utilisateurs */}
            <section className="space-y-4">
                <div className="section-header">
                    <h2 className="section-title flex items-center gap-2">
                        <Users className="w-5 h-5" /> Utilisateurs
                    </h2>
                    <span className="section-count">
                        {users.length} utilisateur{users.length > 1 ? "s" : ""}
                    </span>
                </div>
                {users.length === 0 ? (
                    <EmptyState icon={Users} title="Aucun utilisateur associé" />
                ) : (
                    <GenericTable columns={userColumns} data={users} />
                )}

                <button
                    onClick={() => setModal(true)}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl border border-cyan-500/40 bg-cyan-500/10 text-cyan-200 text-sm font-semibold hover:bg-cyan-500/20 transition-colors"
                >
                    <Download className="w-4 h-4" /> Exporter
                </button>
                
            </section>
            <ExportModal
                open={modal}
                onClose={() => setModal(false)}
                onExportPdf={() => handleExport('pdf')}
                onExportExcel={() => handleExport('excel')}
            />
        </PageLayout>

    );
}

export default DetailImprimante;