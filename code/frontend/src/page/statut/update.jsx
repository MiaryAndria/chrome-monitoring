import { useState, useEffect } from 'react';
import { updateStatut, getDetailStatut } from '../../fonction/statutFonction';
import { useNavigate, useParams } from 'react-router-dom';
import { Pencil, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';
import '../../css/configuration.css';

function StatutUpdate() {
    const [nom, setNom] = useState('');
    const [existedNom, setExistedNom] = useState('');
    const navigate = useNavigate();
    const { id } = useParams();

    const getDetail = async (id) => {
        try {
            const d = await getDetailStatut(id);
            setExistedNom(d.nom);
        } catch (e) {
            console.log(e);
        }
    };

    const updStatut = async () => {
        try {
            const nouveauNom = nom === '' ? existedNom : nom;
            await updateStatut(id, nouveauNom);
            navigate('/liste/statut');
        } catch (e) {
            const msg = e?.response?.data?.detail || "Erreur lors de la mise à jour du statut.";
            window.alert(msg);
        }
    };

    useEffect(() => {
        getDetail(id);
    }, [id]);

    return (
        <PageLayout
            title="Modifier le statut"
            subtitle={`Mise à jour du statut #${id}`}
            titleIcon={Pencil}
        >
            <div className="config-form-container">
                <div className="config-form">
                    <div className="config-form-title">
                        <div className="config-form-title-icon">
                            <Pencil className="w-5 h-5" />
                        </div>
                        Modifier le statut {existedNom}
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Nom</label>
                        <input
                            type="text"
                            className="config-form-input"
                            value={nom}
                            onChange={(e) => setNom(e.target.value)}
                            placeholder={existedNom}
                        />
                    </div>

                    <div className="config-form-actions">
                        <button onClick={() => navigate('/liste/statut')} className="config-btn config-btn-ghost">
                            <ArrowLeft className="w-4 h-4" /> Retour
                        </button>
                        <button onClick={updStatut} className="config-btn config-btn-primary">
                            <Pencil className="w-4 h-4" /> Mettre à jour
                        </button>
                    </div>
                </div>
            </div>
        </PageLayout>
    );
}

export default StatutUpdate;
