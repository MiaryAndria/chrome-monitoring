import { useState, useEffect } from 'react';
import { updateSeuil, getDetailSeuil, updateLimiteTypeSeuil } from '../../fonction/seuilFonction';
import { useNavigate, useParams } from 'react-router-dom';
import { Pencil, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import SelectDropdown from '../component/SelectDropdown';
import '../../css/liste.css';
import '../../css/configuration.css';

function SeuilUpdate() {
    const [valeur, setValeur] = useState('');
    const [sens, setSens] = useState('');
    const [limite, setLimite] = useState(null);
    const [limiteInput, setLimiteInput] = useState('');
    const [unite, setUnite] = useState('%');
    const [existedCle, setExistedCle] = useState('');
    const [existedIdType, setExistedIdType] = useState('');
    const [existedValeur, setExistedValeur] = useState('');
    const navigate = useNavigate();
    const { id } = useParams();

    const getDetail = async (id) => {
        try {
            const d = await getDetailSeuil(id);
            setExistedCle(d.cle);
            setExistedIdType(d.id_type);
            setExistedValeur(d.valeur);
            setSens(d.sens || '>');
            setLimite(d.limite ?? null);
            setLimiteInput(d.limite == null ? '' : String(d.limite));
            setUnite(d.unite || '%');
        } catch (e) {
            console.log(e);
        }
    };

    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const updSeuil = async () => {
        setError(null);
        setSuccess(null);
        const nouvelleValeur = valeur === '' ? existedValeur : valeur;
        try {
            await updateSeuil(id, existedIdType, nouvelleValeur, sens || undefined);
            navigate('/liste/seuil');
        } catch (e) {
            setError(e?.response?.data?.error || e?.response?.data?.detail || "Erreur lors de la mise à jour du seuil.");
        }
    };

    const updLimite = async () => {
        setError(null);
        setSuccess(null);
        try {
            const limiteValeur = limiteInput === '' ? null : Number(limiteInput);
            const res = await updateLimiteTypeSeuil(existedIdType, limiteValeur);
            const data = res?.data || {};
            setLimite(data.limite ?? null);
            setLimiteInput(data.limite == null ? '' : String(data.limite));
            setSuccess("Limite du type de seuil mise à jour.");
        } catch (e) {
            setError(e?.response?.data?.error || e?.response?.data?.detail || "Erreur lors de la mise à jour de la limite.");
        }
    };

    useEffect(() => {
        getDetail(id);
    }, [id]);

    return (
        <PageLayout
            title="Modifier le seuil"
            subtitle={`Mise à jour du seuil #${id}`}
            titleIcon={Pencil}
        >
            <div className="config-form-container">
                <div className="config-form">
                    <div className="config-form-title">
                        <div className="config-form-title-icon">
                            <Pencil className="w-5 h-5" />
                        </div>
                        Modifier le seuil {existedCle}
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Type</label>
                        <input
                            type="text"
                            className="config-form-input"
                            value={existedCle}
                            disabled
                        />
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">
                            Valeur {unite === '%' ? '(%)' : '(entier)'}
                        </label>
                        <input
                            type="number"
                            className="config-form-input"
                            value={valeur}
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder={String(existedValeur ?? '')}
                            min={0}
                            max={limite ?? undefined}
                            step={1}
                        />
                        <p className="text-xs text-zinc-500 mt-1">
                            Unité : {unite === '%' ? 'pourcentage (%)' : 'valeur entière (int)'}
                            {limite !== null && limite !== undefined ? ` — limite max actuelle : ${limite}${unite === '%' ? ' %' : ''}` : ' — aucune limite définie'}
                        </p>
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Sens de comparaison</label>
                        <SelectDropdown
                            options={[
                                { value: '>', label: 'Supérieur au seuil (>)' },
                                { value: '<', label: 'Inférieur au seuil (<)' },
                            ]}
                            value={sens}
                            onChange={(value) => setSens(value)}
                            placeholder="Choisir le sens"
                        />
                    </div>

                    <div className="config-form-group border-t border-white/10 pt-4">
                        <label className="config-form-label">
                            Limite du type de seuil {unite === '%' ? '(%)' : '(entier)'}
                        </label>
                        <input
                            type="number"
                            className="config-form-input"
                            value={limiteInput}
                            onChange={(e) => setLimiteInput(e.target.value)}
                            placeholder={limite == null ? 'Aucune limite' : String(limite)}
                            min={0}
                            step={1}
                        />
                        <p className="text-xs text-zinc-500 mt-1">
                            La limite doit être supérieure ou égale à la valeur du seuil.
                        </p>
                        <div className="mt-2">
                            <button type="button" onClick={updLimite} className="config-btn config-btn-ghost">
                                <Pencil className="w-4 h-4" /> Mettre à jour la limite
                            </button>
                        </div>
                    </div>

                    {error && (
                        <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                            {error}
                        </p>
                    )}
                    {success && (
                        <p className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 p-2.5 rounded-lg">
                            {success}
                        </p>
                    )}

                    <div className="config-form-actions">
                        <button onClick={() => navigate('/liste/seuil')} className="config-btn config-btn-ghost">
                            <ArrowLeft className="w-4 h-4" /> Retour
                        </button>
                        <button onClick={updSeuil} className="config-btn config-btn-primary">
                            <Pencil className="w-4 h-4" /> Mettre à jour la valeur
                        </button>
                    </div>
                </div>
            </div>
        </PageLayout>
    );
}

export default SeuilUpdate;
