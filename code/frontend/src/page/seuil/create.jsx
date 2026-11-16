import { useState, useEffect } from 'react';
import { createSeuil, getListeCategorieSeuil, getListeTypeSeuil } from '../../fonction/seuilFonction';
import { useNavigate } from 'react-router-dom';
import { Plus, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import SelectDropdown from '../component/SelectDropdown';
import '../../css/liste.css';
import '../../css/configuration.css';

function SeuilCreate() {
    const [categories, setCategories] = useState([]);
    const [types, setTypes] = useState([]);
    const [idCategorie, setIdCategorie] = useState('');
    const [idType, setIdType] = useState('');
    const [valeur, setValeur] = useState('');
    const navigate = useNavigate();

    const typeSelectionne = types.find((t) => String(t.id) === String(idType));
    const limite = typeSelectionne?.limite;

    const chargerCategories = async () => {
        const data = await getListeCategorieSeuil();
        setCategories(data || []);
    };

    const chargerTypes = async (idCat) => {
        if (!idCat) {
            setTypes([]);
            setIdType('');
            return;
        }
        const data = await getListeTypeSeuil(idCat);
        setTypes(data || []);
        setIdType('');
    };

    const changerCategorie = (idCat) => {
        setIdCategorie(idCat);
        chargerTypes(idCat);
    };

    const [error, setError] = useState(null);
    const unite = typeSelectionne?.unite || (limite === 100 || limite === null ? '%' : 'int');
    const creerSeuil = async () => {
        setError(null);
        try {
            await createSeuil(idType ? Number(idType) : null, valeur === '' ? null : Number(valeur));
            navigate('/liste/seuil');
        } catch (e) {
            setError(e?.response?.data?.error || e?.response?.data?.detail || "Erreur lors de la création du seuil.");
        }
    };

    useEffect(() => {
        chargerCategories();
    }, []);

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
                        <label className="config-form-label">Catégorie</label>
                        <SelectDropdown
                            options={categories.map((c) => ({ value: String(c.id), label: c.categorie }))}
                            value={idCategorie}
                            onChange={changerCategorie}
                            placeholder="-- Choisir une catégorie --"
                        />
                    </div>
                    {idCategorie ? (
                        <div className="config-form-group">
                            <label className="config-form-label">Type</label>
                            <SelectDropdown
                                options={types.map((t) => ({ value: String(t.id), label: t.type }))}
                                value={idType}
                                onChange={(value) => setIdType(value)}
                                placeholder="-- Choisir un type --"
                            />
                        </div>
                    ) : (
                        <div>
                            <p>Choisissez d'abord une catégorie</p>
                        </div>
                    )}
                    <div className="config-form-group">
                        <label className="config-form-label">
                            Valeur {typeSelectionne ? (unite === '%' ? '(%)' : '(entier)') : ''}
                        </label>
                        <input
                            type="number"
                            className="config-form-input"
                            value={valeur}
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder="Entrer valeur"
                            min={0}
                            max={limite ?? undefined}
                            step={1}
                        />
                        {typeSelectionne && (
                            <p className="text-xs text-zinc-500 mt-1">
                                Unité : {unite === '%' ? 'pourcentage (%)' : 'valeur entière (int)'}
                                {limite !== null && limite !== undefined ? ` — limite max : ${limite}${unite === '%' ? ' %' : ''}` : ' — aucune limite définie'}
                            </p>
                        )}
                    </div>

                    {error && (
                        <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                            {error}
                        </p>
                    )}

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
