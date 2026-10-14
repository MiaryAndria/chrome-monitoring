import { useState, useEffect } from 'react';
import { getListeArchiver, restaurerConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';
import { Archive, RotateCcw } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import '../../css/liste.css';
import '../../css/configuration.css';

function ArchivedConfiguration() {
    const [conf, setConf] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const getConfiguration = async () => {
        try {
            setLoading(true);
            const response = await getListeArchiver();
            setConf(Array.isArray(response?.data) ? response.data : []);
        } catch (e) {
            console.log('Erreur récupération configuration archivée :', e);
        } finally {
            setLoading(false);
        }
    };

    const restaurer = async (id) => {
        try {
            await restaurerConfiguration(id);
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
                    <button onClick={() => restaurer(c.id)} className="config-btn config-btn-success" style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}>
                        <RotateCcw className="w-3.5 h-3.5" /> Restaurer
                    </button>
                </div>
            )
        }
    ];

    return (
        <PageLayout
            title="Configurations archivées"
            subtitle="Configurations supprimées pouvant être restaurées"
            titleIcon={Archive}
        >
            <div className="space-y-6">
                {loading ? (
                    <div className="flex justify-center p-12">
                        <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                    </div>
                ) : !conf || conf.length === 0 ? (
                    <div className="empty-state">
                        <Archive className="empty-state-icon" />
                        <p className="empty-state-title">Aucune configuration archivée.</p>
                        <p className="empty-state-subtitle">Aucune donnée archivée n'est disponible.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des configurations archivées</h2>
                                <span className="section-count">{conf.length} archivée(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={conf} />
                    </>
                )}
            </div>
        </PageLayout>
    );
}

export default ArchivedConfiguration;
