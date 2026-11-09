import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, GitCompare } from "lucide-react";
import PageLayout from "../../components/PageLayout";
import SelectDropdown from "../component/SelectDropdown";
import DeviceSelector from "./DeviceSelector";
import ComparaisonResult from "./ComparaisonResult";
import ComparaisonChart from "./ComparaisonChart";
import { listeDeviceVersion, effectuerComparaisonSimple } from "../../fonction/comparaisonFonction";
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

function ComparaisonSingle() {
    const navigate = useNavigate();
    const [selection, setSelection] = useState([]);
    const [versions, setVersions] = useState([]);
    const [versionA, setVersionA] = useState("");
    const [versionB, setVersionB] = useState("");
    const [resultat, setResultat] = useState(null);
    const [labels, setLabels] = useState({ a: "A", b: "B" });
    const [erreur, setErreur] = useState("");
    const [chargement, setChargement] = useState(false);

    const device = selection[0] || null;
    const options = toOptions(versions);

    const chargerVersions = async () => {
        setVersionA("");
        setVersionB("");
        setResultat(null);
        setErreur("");

        if (!device) {
            setVersions([]);
            return;
        }

        try {
            const data = await listeDeviceVersion(device.id);
            const liste = data || [];
            setVersions(liste);
            const opts = toOptions(liste);
            setVersionA(opts.length ? opts[opts.length - 1].value : "");
            setVersionB(opts.length > 1 ? opts[opts.length - 2].value : "");
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        chargerVersions();
    }, [device?.id]);

    const comparer = async () => {
        setErreur("");
        if (!device) { setErreur("Sélectionnez un appareil."); return; }
        if (!versionA || !versionB) { setErreur("Choisissez deux versions."); return; }
        if (versionA === versionB) { setErreur("Choisissez deux versions différentes."); return; }
        try {
            setChargement(true);
            const res = await effectuerComparaisonSimple(device.id, versionA, versionB);
            setResultat(res?.resultat || null);
            setLabels({
                a: `${device.serial_number} · ${versionA}`,
                b: `${device.serial_number} · ${versionB}`,
            });
        } catch (e) {
            setErreur(e?.response?.data?.detail || "Erreur lors de la comparaison.");
        } finally {
            setChargement(false);
        }
    };

    return (
        <PageLayout
            title="Comparaison simple"
            subtitle="Un appareil, deux versions de ChromeOS"
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
            <DeviceSelector maxSelection={1} selection={selection} onSelectionChange={setSelection} />

            {device && (
                <div className="glass-panel rounded-2xl p-5 space-y-4">
                    <div className="text-sm text-zinc-300">
                        Appareil : <span className="font-mono text-zinc-100">{device.serial_number}</span>{" "}
                        <span className="text-zinc-500">({device.modele || "modèle inconnu"})</span>
                    </div>

                    {options.length < 2 ? (
                        <p className="text-xs text-amber-300">
                            Une seule version connue pour cet appareil — comparaison impossible.
                        </p>
                    ) : (
                        <div className="flex flex-wrap items-end gap-4">
                            <div>
                                <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">Version A</div>
                                <SelectDropdown options={options} value={versionA} onChange={setVersionA} placeholder="Choisir" />
                            </div>
                            <div>
                                <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">Version B</div>
                                <SelectDropdown options={options} value={versionB} onChange={setVersionB} placeholder="Choisir" />
                            </div>
                            <button onClick={comparer} disabled={chargement} className={BTN_PRIMAIRE}>
                                {chargement ? "Comparaison…" : "Comparer"}
                            </button>
                        </div>
                    )}

                    {erreur && <p className="text-xs text-red-400">{erreur}</p>}
                </div>
            )}

            <ComparaisonResult resultat={resultat} labels={labels} />
            <ComparaisonChart resultat={resultat} labels={labels} />
        </PageLayout>
    );
}

export default ComparaisonSingle;
