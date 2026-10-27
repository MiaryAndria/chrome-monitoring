import { useState, useEffect } from 'react';
import { updateSeuil, getDetailSeuil } from '../../fonction/seuilFonction';
import { useNavigate, useParams } from 'react-router-dom';
import { Pencil, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';
import '../../css/configuration.css';

function SeuilUpdate() {
    const [cle, setCle] = useState('');
    const [valeur, setValeur] = useState('');
    const [existedCle, setExistedCle] = useState('');
    const [existedValeur, setExistedValeur] = useState('');
    const navigate = useNavigate();
    const { id } = useParams();

    const getDetail = async (id) => {
        try {
            const d = await getDetailSeuil(id);
            setExistedCle(d.cle);
            setExistedValeur(d.valeur);
        } catch (e) {
            console.log(e);
        }
    };

    const updSeuil = async () => {
        try {
            await updateSeuil(id, cle, Number(valeur));
            navigate('/liste/seuil');
        } catch (e) {
            console.log(e);
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
                        <label className="config-form-label">Clé</label>
                        <input
                            type="text"
                            className="config-form-input"
                            onChange={(e) => setCle(e.target.value)}
                            placeholder={existedCle}
                        />
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Valeur</label>
                        <input
                            type="number"
                            className="config-form-input"
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder={existedValeur}
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
