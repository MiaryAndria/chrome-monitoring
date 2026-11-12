import { useState, useEffect } from 'react';
import { updateSeuil, getDetailSeuil } from '../../fonction/seuilFonction';
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
        } catch (e) {
            console.log(e);
        }
    };

    const updSeuil = async () => {
        const nouvelleValeur = valeur === '' ? existedValeur : Number(valeur);
        if (!Number.isInteger(nouvelleValeur) || nouvelleValeur < 0) {
            window.alert("La valeur doit être un nombre entier positif.");
            return;
        }
        if (limite !== null && limite !== undefined && nouvelleValeur > limite) {
            window.alert(`La valeur ne peut pas dépasser ${limite} pour ce type de seuil.`);
            return;
        }
        try {
            await updateSeuil(id, existedIdType, nouvelleValeur, sens || undefined);
            navigate('/liste/seuil');
        } catch (e) {
            const msg = e?.response?.data?.detail || "Erreur lors de la mise à jour du seuil.";
            window.alert(msg);
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
                        <label className="config-form-label">Valeur</label>
                        <input
                            type="number"
                            className="config-form-input"
                            value={valeur}
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder={existedValeur}
                            min={0}
                            max={limite ?? undefined}
                        />
                        {limite !== null && limite !== undefined && (
                            <p className="text-xs text-zinc-500 mt-1">
                                Valeur maximale pour ce type : {limite}
                            </p>
                        )}
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

                    <div className="config-form-actions">
                        <button onClick={() => navigate('/liste/seuil')} className="config-btn config-btn-ghost">
                            <ArrowLeft className="w-4 h-4" /> Retour
                        </button>
                        <button onClick={updSeuil} className="config-btn config-btn-primary">
                            <Pencil className="w-4 h-4" /> Mettre à jour
                        </button>
                    </div>
                </div>
            </div>
        </PageLayout>
    );
}

export default SeuilUpdate;
