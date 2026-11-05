import { useEffect, useState } from "react";
import { Search, Laptop } from "lucide-react";
import TableSkeleton from "../../components/skeletons/TableSkeleton";
import EmptyState from "../../components/EmptyState";
import Pagination from "../../components/Pagination";
import usePaginatedData from "../../hooks/usePaginatedData";
import useDebounce from "../../hooks/useDebounce";
import FilialeDropdown from "../component/FilialeDropdown";
import StatutDropdown from "../component/StatutDropdown";
import UtilisateurDropDown from "../component/UtilisateurDropDown";
import ResetFiltreButton from "../component/ResetFiltreButton";
import { getListeDevice, getListeStatut, getModeles, getBadgeClass } from "../../fonction/deviceFonction";
import { getListeFiliale } from "../../fonction/filialeFonction";
import { getListeUtilisateurRecent } from "../../fonction/userFonction";

/**
 * Sélecteur d'appareils : filtres (filiale / modèle / utilisateur) + recherche par
 * numéro de série (toujours active), table paginée avec cases à cocher.
 *
 * Props :
 *  - maxSelection        : 1 (simple) ou 2 (double)
 *  - selection           : tableau d'appareils sélectionnés (contrôlé par le parent)
 *  - onSelectionChange   : setter appelé avec le nouveau tableau
 */
function DeviceSelector({ maxSelection = 1, selection = [], onSelectionChange }) {
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);

    const [search, setSearch] = useState("");
    const debouncedSearch = useDebounce(search, 300);

    const [listeFiliales, setListeFiliales] = useState([]);
    const [filiale, setFiliale] = useState("");
    const [listeStatuts, setListeStatuts] = useState([]);
    const [statut, setStatut] = useState("");
    const [modeles, setModeles] = useState([]);
    const [modele, setModele] = useState("");
    const [listeUtilisateurRecent, setListeUtilisateurRecent] = useState([]);
    const [utilisateurRecent, setUtilisateurRecent] = useState("");

    const chargerFiltres = async () => {
        try {
            const filiales = await getListeFiliale();
            const statuts = await getListeStatut();
            const modelesListe = await getModeles();
            const utilisateurs = await getListeUtilisateurRecent();
            setListeFiliales(filiales || []);
            setListeStatuts(statuts || []);
            setModeles(modelesListe || []);
            setListeUtilisateurRecent(utilisateurs || []);
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        chargerFiltres();
    }, []);

    const { items: devices, total, totalPages, loading } = usePaginatedData(
        getListeDevice,
        currentPage,
        pageSize,
        {
            filiale: filiale || undefined,
            statut: statut || undefined,
            modele: modele || undefined,
            utilisateur_recent: utilisateurRecent || undefined,
            recherche: debouncedSearch || undefined,
        }
    );

    useEffect(() => {
        setCurrentPage(1);
    }, [filiale, statut, modele, utilisateurRecent, debouncedSearch]);

    const estSelectionne = (d) => selection.some((s) => s.id === d.id);
    const complet = selection.length >= maxSelection;
    const verrouille = (d) => complet && !estSelectionne(d) && maxSelection !== 1;

    const toggle = (d) => {
        if (estSelectionne(d)) {
            onSelectionChange(selection.filter((s) => s.id !== d.id));
            return;
        }
        if (complet) {
            if (maxSelection === 1) onSelectionChange([d]);
            return;
        }
        onSelectionChange([...selection, d]);
    };

    const filtresActifs =
        filiale !== "" || statut !== "" || modele !== "" || utilisateurRecent !== "" || search !== "";

    const reinitialiser = () => {
        setFiliale("");
        setStatut("");
        setModele("");
        setUtilisateurRecent("");
        setSearch("");
        setCurrentPage(1);
    };

    return (
        <div className="space-y-4">
            <div className="glass-panel rounded-2xl p-5 relative z-50">
                <div className="relative max-w-md mb-4">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <input
                        type="text"
                        placeholder="Rechercher par numéro de série…"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-900/60 border border-white/10 text-zinc-200 text-sm placeholder-zinc-500 focus:outline-none focus:border-cyan-400/50"
                    />
                </div>
                <div className="flex flex-wrap items-center gap-3">
                    <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Filiale :</span>
                    <FilialeDropdown listeFiliales={listeFiliales} filiale={filiale} setFiliale={setFiliale} />

                    <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider ml-2">Modèle :</span>
                    <StatutDropdown
                        listeStatuts={modeles.map((m) => ({ nom: m }))}
                        statut={modele}
                        setStatut={setModele}
                        labelTous="Tous les modèles"
                    />

                    <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider ml-2">Utilisateur :</span>
                    <UtilisateurDropDown
                        listeUtilisateurRecent={listeUtilisateurRecent}
                        utilisateurRecent={utilisateurRecent}
                        setUtilisateurRecent={setUtilisateurRecent}
                    />

                    <ResetFiltreButton actif={filtresActifs} onClick={reinitialiser} />
                </div>
            </div>

            <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-500">
                    {total} appareil(s) — {selection.length}/{maxSelection} sélectionné(s)
                </span>
                {maxSelection === 2 && selection.length === 2 && (
                    <span className="text-xs text-emerald-400">Deux appareils sélectionnés</span>
                )}
            </div>

            {loading && devices.length === 0 ? (
                <TableSkeleton />
            ) : devices.length === 0 ? (
                <EmptyState
                    icon={Laptop}
                    title="Aucun appareil trouvé"
                    subtitle="Modifiez les filtres ou la recherche par numéro de série."
                />
            ) : (
                <div className="overflow-x-auto w-full glass-panel border border-white/10 rounded-xl">
                    <table className="w-full text-left text-sm text-zinc-300">
                        <thead className="text-[10px] uppercase bg-white/5 text-zinc-400 border-b border-white/10 tracking-wider font-semibold">
                            <tr>
                                <th className="px-4 py-4 w-12"></th>
                                <th className="px-5 py-4">Modèle</th>
                                <th className="px-5 py-4">N° Série</th>
                                <th className="px-5 py-4">Filiale</th>
                                <th className="px-5 py-4">OS</th>
                                <th className="px-5 py-4">Statut</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {devices.map((d) => (
                                <tr
                                    key={d.id}
                                    className={`transition-colors ${estSelectionne(d) ? "bg-purple-500/10" : "hover:bg-white/5"}`}
                                >
                                    <td className="px-4 py-3">
                                        <label className="flex items-center cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={estSelectionne(d)}
                                                disabled={verrouille(d)}
                                                onChange={() => toggle(d)}
                                                className="disabled:opacity-30"
                                            />
                                        </label>
                                    </td>
                                    <td className="px-5 py-3">{d.modele || "—"}</td>
                                    <td className="px-5 py-3 font-mono text-zinc-300">{d.serial_number || "—"}</td>
                                    <td className="px-5 py-3 text-zinc-400">{d.filiale || "—"}</td>
                                    <td className="px-5 py-3 text-zinc-400">{d.chromeos_version || "—"}</td>
                                    <td className="px-5 py-3">
                                        <span className={`badge badge-sm ${getBadgeClass(d.status || d.nom_statut || "UNKNOWN")}`}>
                                            {d.status || d.nom_statut || "UNKNOWN"}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <Pagination
                page={currentPage}
                pageSize={pageSize}
                totalPages={totalPages}
                total={total}
                loading={loading}
                onPageChange={setCurrentPage}
                onPageSizeChange={(size) => {
                    setPageSize(size);
                    setCurrentPage(1);
                }}
            />
        </div>
    );
}

export default DeviceSelector;
