import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, GitCompare, FileDown, FileSpreadsheet } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import ComparaisonResult from "./ComparaisonResult";
import ComparaisonChart from "./ComparaisonChart";
import { getComparaisonDetail } from "../../fonction/comparaisonFonction";
import { telechargerFichier } from "../../fonction/exportFonction";
import "../../css/liste.css";
import "../../css/filiale.css";

function ComparaisonDetail() {
    const navigate = useNavigate();
    const { id } = useParams();
    const [detail, setDetail] = useState(null);
    const [chargement, setChargement] = useState(true);
    const [erreur, setErreur] = useState("");

    const chargerDetail = async () => {
        try {
            setChargement(true);
            const data = await getComparaisonDetail(id);
            setDetail(data || null);
        } catch (e) {
            setErreur(e?.response?.data?.detail || "Comparaison introuvable.");
        } finally {
            setChargement(false);
        }
    };

    useEffect(() => {
        chargerDetail();
    }, [id]);

    const exporter = async (format) => {
        try {
            const nom = `comparaison_${id}.${format === "pdf" ? "pdf" : "xlsx"}`;
            await telechargerFichier(`/comparaison/${id}/export/${format}`, nom);
        } catch (e) {
            setErreur("Erreur lors de l'export.");
        }
    };

    const labels = detail
        ? {
              a: `${detail.device_a || detail.id_device_a} · ${detail.version_a || "—"}`,
              b: `${detail.device_b || detail.id_device_b} · ${detail.version_b || "—"}`,
          }
        : { a: "A", b: "B" };

    return (
        <PageLayout
            title="Détail de la comparaison"
            subtitle={
                detail?.date_comparaison
                    ? new Date(detail.date_comparaison).toLocaleString("fr-FR")
                    : ""
            }
            titleIcon={GitCompare}
            headerRight={
                <button
                    onClick={() => navigate("/comparaison/liste")}
                    className="px-3 py-1.5 text-xs font-semibold text-zinc-300 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all"
                >
                    <ArrowLeft className="inline w-3.5 h-3.5 mr-1" /> Retour
                </button>
            }
            contentClassName="space-y-6"
        >
            {chargement ? (
                <p className="text-sm text-zinc-500">Chargement…</p>
            ) : erreur ? (
                <p className="text-sm text-red-400">{erreur}</p>
            ) : !detail ? (
                <p className="text-sm text-zinc-500">Comparaison introuvable.</p>
            ) : (
                <>
                    <div className="glass-panel rounded-2xl p-4 flex items-center justify-between gap-3">
                        <span className="text-xs text-zinc-400">
                            Type : {detail.id_type_comparaison === 1 ? "Simple" : "Double"}
                        </span>
                        <div className="flex gap-2">
                            <button
                                onClick={() => exporter("pdf")}
                                className="px-3 py-1.5 text-xs font-semibold text-red-300 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-xl transition-all"
                            >
                                <FileDown className="inline w-3.5 h-3.5 mr-1" /> PDF
                            </button>
                            <button
                                onClick={() => exporter("excel")}
                                className="px-3 py-1.5 text-xs font-semibold text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 rounded-xl transition-all"
                            >
                                <FileSpreadsheet className="inline w-3.5 h-3.5 mr-1" /> Excel
                            </button>
                        </div>
                    </div>

                    {detail.resultat ? (
                        <>
                            <ComparaisonResult resultat={detail.resultat} labels={labels} />
                            <ComparaisonChart resultat={detail.resultat} labels={labels} />
                        </>
                    ) : (
                        <p className="text-sm text-zinc-500">Aucun résultat enregistré pour cette comparaison.</p>
                    )}
                </>
            )}
        </PageLayout>
    );
}

export default ComparaisonDetail;
