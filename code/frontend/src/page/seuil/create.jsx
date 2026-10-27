import { useState } from 'react';
import { createSeuil } from '../../fonction/seuilFonction';
import { useNavigate } from 'react-router-dom';
import { Plus, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';
import '../../css/configuration.css';

function SeuilCreate() {
    const [cle, setCle] = useState('');
    const [valeur, setValeur] = useState('');
    const navigate = useNavigate();

    const creerSeuil = async () => {
        try {
            await createSeuil(cle, Number(valeur));
            navigate('/liste/seuil');
        } catch (e) {
            console.log(e);
        }
    };

    return (
        <PageLayout
            title="Créer un seuil"
            subtitle="Ajouter un nouveau seuil au système"
            titleIcon={Plus}
        >
            <div className="config-form-container">
                <div className="config-form">
                    <div className="config-form-title">
                        <div className="config-form-title-icon">
                            <Plus className="w-5 h-5" />
                        </div>
                        Nouveau seuil
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Clé</label>
                        <input
                            type="text"
                            className="config-form-input"
                            onChange={(e) => setCle(e.target.value)}
                            placeholder="Entrer clé seuil"
                        />
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Valeur</label>
                        <input
                            type="number"
                            className="config-form-input"
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder="Entrer valeur"
                        />
                    </div>

                    <div className="config-form-actions">
                        <button onClick={() => navigate('/liste/seuil')} className="config-btn config-btn-ghost">
                            <ArrowLeft className="w-4 h-4" /> Retour
                        </button>
                        <button onClick={creerSeuil} className="config-btn config-btn-primary">
                            <Plus className="w-4 h-4" /> Créer
                        </button>
                    </div>
                </div>
            </div>
        </PageLayout>
    );
}

export default SeuilCreate;
