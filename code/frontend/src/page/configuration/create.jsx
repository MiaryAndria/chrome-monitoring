import { useState, useEffect } from 'react';
import { createConfiguration, getListeCategorieConfiguration, getListeTypeConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';
import { Plus, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';
import '../../css/configuration.css';

function ConfigurationCreate() {
    const [categories, setCategories] = useState([]);
    const [types, setTypes] = useState([]);
    const [idCategorie, setIdCategorie] = useState('');
    const [idType, setIdType] = useState('');
    const [valeur, setValeur] = useState('');
    const navigate = useNavigate();

    const chargerCategories = async () => {
        const data = await getListeCategorieConfiguration();
        setCategories(data || []);
    };

    const chargerTypes = async (idCat) => {
        if (!idCat) {
            setTypes([]);
            setIdType('');
            return;
        }
        const data = await getListeTypeConfiguration(idCat);
        setTypes(data || []);
        setIdType('');
    };

    const changerCategorie = (e) => {
        const idCat = e.target.value;
        setIdCategorie(idCat);
        chargerTypes(idCat);
    };

    const creerConfiguration = async () => {
        try {
            await createConfiguration(Number(idType), valeur);
            navigate('/liste/configuration');
        } catch (e) {
            const msg = e?.response?.data?.detail || "Erreur lors de la création de la configuration.";
            window.alert(msg);
        }
    };

    useEffect(() => {
        chargerCategories();
    }, []);

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
                        <label className="config-form-label">Catégorie</label>
                        <select
                            className="config-form-input"
                            value={idCategorie}
                            onChange={changerCategorie}
                        >
                            <option value="">-- Choisir une catégorie --</option>
                            {categories.map((c) => (
                                <option key={c.id} value={c.id}>{c.categorie}</option>
                            ))}
                        </select>
                    </div>
                    {idCategorie ? (
                        <div className="config-form-group">
                            <label className="config-form-label">Type</label>
                            <select
                                className="config-form-input"
                                value={idType}
                                onChange={(e) => setIdType(e.target.value)}
                            >
                                <option value="">-- Choisir un type --</option>
                                {types.map((t) => (
                                    <option key={t.id} value={t.id}>{t.type}</option>
                                ))}
                            </select>
                        </div>
                    ) : (
                        <div>
                            <p>Choisissez d'abord une catégorie</p>
                        </div>
                    )}
                    <div className="config-form-group">
                        <label className="config-form-label">Valeur</label>
                        <input
                            type="text"
                            className="config-form-input"
                            value={valeur}
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
