import { useState, useEffect } from 'react';
import { getListeConfiguration, deleteConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';
import { Settings, Plus, Pencil, Trash2 } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import '../../css/liste.css';
import '../../css/configuration.css';

function ConfigurationListe() {
    const [conf, setConf] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const getConfiguration = async () => {
        try {
            setLoading(true);
            const response = await getListeConfiguration();
            setConf(Array.isArray(response?.data) ? response.data : []);
        } catch (e) {
            console.log('Erreur récupération configuration :', e);
        } finally {
            setLoading(false);
        }
    };

    const supprimerConfiguration = async (id) => {
        try {
            await deleteConfiguration(id);
            await getConfiguration();
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(() => {
        getConfiguration();
    }, []);

    const columns = [
        { header: 'Type', render: (c) => <span className="font-bold text-zinc-100">{c.type}</span> },
        { header: 'Valeur', render: (c) => <span className="text-zinc-300">{c.valeur}</span> },
        { header: 'Date', render: (c) => <span className="text-zinc-400 text-xs font-mono">{c.date ? new Date(c.date).toLocaleString() : '-'}</span> },
        {
            header: 'Actions', render: (c) => (
                <div className="config-table-actions">
                    <button onClick={() => navigate(`/update/configuration/${c.id}`)} className="config-btn config-btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Pencil className="w-3.5 h-3.5" /> Modifier
                    </button>
                    <button onClick={() => supprimerConfiguration(c.id)} className="config-btn config-btn-danger" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <Trash2 className="w-3.5 h-3.5" /> Supprimer
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Configurations"
            subtitle="Gérer les configurations du système"
            titleIcon={Settings}
            headerRight={
                <button onClick={() => navigate('/creer/configuration')} className="config-btn config-btn-primary">
                    <Plus className="w-4 h-4" /> Créer configuration
                </button>
            }
        >
            <div className="space-y-6">
                {loading && conf.length === 0 ? (
                    <TableSkeleton />
                ) : !conf || conf.length === 0 ? (
                    <div className="empty-state">
                        <Settings className="empty-state-icon" />
                        <p className="empty-state-title">Aucune configuration trouvée.</p>
                        <p className="empty-state-subtitle">Aucune donnée de configuration n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des configurations</h2>
                                <span className="section-count">{conf.length} configuration(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={conf} />
                    </>
                )}
            </div>
        </PageLayout>
    );
}

export default ConfigurationListe;
