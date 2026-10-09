import { useState, useEffect } from 'react';
import { getListeConfiguration } from '../../fonction/configurationFonction';
import { useNavigate } from 'react-router-dom';

function archivedConfiguration() {
    const [conf, setConf] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate= useNavigate();

    const getConfiguration = async () => {
        try {
            setLoading(true);

            const response = await getListeConfiguration();

            setConf(response.data);
        } catch (e) {
            console.log("Erreur récupération configuration :", e);
        } finally {
            setLoading(false);
        }
    };

    const creerConfiguration = async()=>{
        try{
            navigate('/creer/configuration')
        }catch(e){
            console.log(e)
        }
    }

    useEffect(() => {
        getConfiguration();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center p-12">
                <span className="loading loading-infinity loading-lg text-cyan-500"></span>
            </div>
        );
    }

    if (conf.length === 0) {
        return (
            <div className="empty-state">
                <p className="empty-state-title">
                    Aucune configuration trouvée.
                </p>
                <p className="empty-state-subtitle">
                    Aucune donnée de configuration n'est disponible.
                </p>
            </div>
        );
    }

    return (
        <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">
                Configurations
            </h2>

            <div className="overflow-x-auto">
                <table className="table w-full">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Valeur</th>
                        </tr>
                    </thead>

                    <tbody>
                        {conf.map((configuration) => (
                            <tr key={configuration.id}>
                                <td>{configuration.type}</td>
                                <td>{configuration.valeur}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <button onClick={creerConfiguration}></button>
        </div>
    );
}

export default archivedConfiguration;

