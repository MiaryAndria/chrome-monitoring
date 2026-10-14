import { useState } from 'react';
import { createConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';
import { Plus, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';
import '../../css/configuration.css';

function ConfigurationCreate() {
    const [type, setType] = useState('');
    const [valeur, setValeur] = useState('');
    const navigate = useNavigate();

    const creerConfiguration = async () => {
        try {
            await createConfiguration(type, valeur);
            navigate('/liste/configuration');
        } catch (e) {
            console.log(e);
        }
    };

    return (
        <PageLayout
            title="Créer une configuration"
            subtitle="Ajouter une nouvelle configuration au système"
            titleIcon={Plus}
        >
            <div className="config-form-container">
                <div className="config-form">
                    <div className="config-form-title">
                        <div className="config-form-title-icon">
                            <Plus className="w-5 h-5" />
                        </div>
                        Nouvelle configuration
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Type</label>
                        <input
                            type="text"
                            className="config-form-input"
                            onChange={(e) => setType(e.target.value)}
                            placeholder="Entrer type configuration"
                        />
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Valeur</label>
                        <input
                            type="text"
                            className="config-form-input"
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder="Entrer valeur"
                        />
                    </div>

                    <div className="config-form-actions">
                        <button onClick={() => navigate('/liste/configuration')} className="config-btn config-btn-ghost">
                            <ArrowLeft className="w-4 h-4" /> Retour
                        </button>
                        <button onClick={creerConfiguration} className="config-btn config-btn-primary">
                            <Plus className="w-4 h-4" /> Créer
                        </button>
                    </div>
                </div>
            </div>
        </PageLayout>
    );
}

export default ConfigurationCreate;
