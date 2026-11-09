import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, GitCompare } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import SelectDropdown from "../component/SelectDropdown";
import DeviceSelector from "./DeviceSelector";
import ComparaisonResult from "./ComparaisonResult";
import ComparaisonChart from "./ComparaisonChart";
import { listeDeviceVersion, effectuerDoubleComparaison } from "../../fonction/comparaisonFonction";
import "../../css/liste.css";
import "../../css/filiale.css";

const BTN_PRIMAIRE =
    "px-4 py-2 text-sm font-semibold rounded-xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/25 transition-all disabled:opacity-40 cursor-pointer";

function toOptions(versions) {
    const vus = new Set();
    const options = [];
    for (const v of versions || []) {
        const valeur = v.chromeos_version;
        if (!valeur || vus.has(valeur)) continue;
        vus.add(valeur);
        options.push({ value: valeur, label: valeur });
    }
    return options;
}

function ComparaisonDouble() {
    const navigate = useNavigate();
    const [selection, setSelection] = useState([]);
    const [versionsParDevice, setVersionsParDevice] = useState({});
    const [versionA, setVersionA] = useState("");
    const [versionB, setVersionB] = useState("");
    const [resultat, setResultat] = useState(null);
    const [labels, setLabels] = useState({ a: "A", b: "B" });
    const [erreur, setErreur] = useState("");
    const [chargement, setChargement] = useState(false);

    const deviceA = selection[0] || null;
    const deviceB = selection[1] || null;
    const idsKey = selection.map((d) => d.id).join(",");

    const chargerVersions = async () => {
        for (const d of selection) {
            if (versionsParDevice[d.id]) continue;
            try {
                const data = await listeDeviceVersion(d.id);
                setVersionsParDevice((prev) => (prev[d.id] ? prev : { ...prev, [d.id]: data || [] }));
            } catch (e) {
                console.log(e);
            }
        }
    };

    const reinitialiserResultat = () => {
        setVersionA("");
        setVersionB("");
        setResultat(null);
        setErreur("");
    };

    useEffect(() => {
        chargerVersions();
        reinitialiserResultat();
    }, [idsKey]);

    const optionsA = toOptions(versionsParDevice[deviceA?.id]);
    const optionsB = toOptions(versionsParDevice[deviceB?.id]);
    const valeurA = versionA || (optionsA.length ? optionsA[optionsA.length - 1].value : "");
    const valeurB = versionB || (optionsB.length ? optionsB[optionsB.length - 1].value : "");

    const comparer = async () => {
        setErreur("");
        if (!deviceA || !deviceB) { setErreur("Sélectionnez deux appareils."); return; }
        if (!valeurA || !valeurB) { setErreur("Choisissez une version pour chaque appareil."); return; }
        try {
            setChargement(true);
            const res = await effectuerDoubleComparaison(deviceA.id, valeurA, deviceB.id, valeurB);
            setResultat(res?.resultat || null);
            setLabels({
                a: `${deviceA.serial_number} · ${valeurA}`,
                b: `${deviceB.serial_number} · ${valeurB}`,
            });
        } catch (e) {
            setErreur(e?.response?.data?.detail || "Erreur lors de la comparaison.");
        } finally {
            setChargement(false);
        }
    };

    return (
        <PageLayout
            title="Comparaison double"
            subtitle="Deux appareils, une version chacun"
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
            <DeviceSelector maxSelection={2} selection={selection} onSelectionChange={setSelection} />

            {(deviceA || deviceB) && (
                <div className="glass-panel rounded-2xl p-5 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <div className="text-sm text-zinc-300">
                                Appareil A :{" "}
                                <span className="font-mono text-zinc-100">{deviceA ? deviceA.serial_number : "—"}</span>
                            </div>
                            {deviceA && (optionsA.length === 0 ? (
                                <p className="text-xs text-amber-300">Aucune version connue.</p>
                            ) : (
                                <SelectDropdown options={optionsA} value={valeurA} onChange={setVersionA} placeholder="Version" />
                            ))}
                        </div>
                        <div className="space-y-2">
                            <div className="text-sm text-zinc-300">
                                Appareil B :{" "}
                                <span className="font-mono text-zinc-100">{deviceB ? deviceB.serial_number : "—"}</span>
                            </div>
                            {deviceB && (optionsB.length === 0 ? (
                                <p className="text-xs text-amber-300">Aucune version connue.</p>
                            ) : (
                                <SelectDropdown options={optionsB} value={valeurB} onChange={setVersionB} placeholder="Version" />
                            ))}
                        </div>
                    </div>

                    <button onClick={comparer} disabled={chargement || !deviceA || !deviceB} className={BTN_PRIMAIRE}>
                        {chargement ? "Comparaison…" : "Comparer"}
                    </button>

                    {erreur && <p className="text-xs text-red-400">{erreur}</p>}
                </div>
            )}

            <ComparaisonResult resultat={resultat} labels={labels} />
            <ComparaisonChart resultat={resultat} labels={labels} />
        </PageLayout>
    );
}

export default ComparaisonDouble;
