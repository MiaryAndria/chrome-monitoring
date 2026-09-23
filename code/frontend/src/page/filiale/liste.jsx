import { useEffect, useState } from "react";
import { Building2, Laptop, ChevronRight, Server, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import '../../css/liste.css';
import '../../css/filiale.css';
import { getListeFiliale } from "../../fonction/filialeFonction";

// Variantes de couleur cycliques — définies uniquement dans le CSS
const CARD_VARIANTS = ['cyan', 'purple', 'emerald', 'amber'];

function getOrgLabel(path) {
    if (!path) return 'Organisation';
    const parts = path.split('/').filter(Boolean);
    return parts[parts.length - 1] || path;
}

function getOrgDepth(path) {
    if (!path) return 0;
    return path.split('/').filter(Boolean).length;
}

function ListeFiliale() {
    const [filiales, setFiliales] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const recupererFiliales = async () => {
        try {
            setLoading(true);
            const data = await getListeFiliale();
            setFiliales(data || []);
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        recupererFiliales();
    }, []);

    return (
        <div className="device-layout" data-theme="dark">
            <MouseSpotlight />
            <Sidebar />

            <div className="flex-1 flex flex-col h-screen overflow-hidden relative z-10">
                <div className="bg-glow-cyan"></div>
                <div className="bg-glow-purple"></div>

                <Navbar />

                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-8 z-10">

                    {/* Stats */}
                    <div className="stats stats-container glass-panel">
                        <div className="stat place-items-center">
                            <div className="stat-title text-zinc-400">Total Filiales</div>
                            <div className="stat-value neon-text-cyan text-4xl">{filiales.length}</div>
                            <div className="stat-desc text-zinc-500 flex items-center gap-1 mt-1">
                                <Building2 className="w-3 h-3 text-emerald-500" /> Unités organisationnelles
                            </div>
                        </div>
                        <div className="stat place-items-center border-t md:border-t-0 md:border-l border-white/5">
                            <div className="stat-title text-zinc-400">Infrastructure</div>
                            <div className="stat-value text-emerald-400 text-4xl">
                                <Activity className="w-8 h-8 mx-auto animate-pulse" />
                            </div>
                            <div className="stat-desc text-zinc-500">Système de suivi actif</div>
                        </div>
                        <div className="stat place-items-center border-t md:border-t-0 md:border-l border-white/5">
                            <div className="stat-title text-zinc-400">Navigation</div>
                            <div className="stat-value text-purple-400 text-4xl">
                                <Laptop className="w-8 h-8 mx-auto" />
                            </div>
                            <div className="stat-desc text-zinc-500">Cliquez sur une filiale pour ses devices</div>
                        </div>
                    </div>

                    {/* Liste filiales */}
                    <div>
                        <div className="section-header">
                            <h2 className="section-title">Filiales &amp; Unités Organisationnelles</h2>
                            <span className="section-count">{filiales.length} unité(s)</span>
                        </div>

                        {loading ? (
                            <div className="flex justify-center p-12">
                                <span className="loading loading-infinity loading-lg text-cyan-500"></span>
                            </div>
                        ) : filiales.length === 0 ? (
                            <div className="empty-state">
                                <Building2 className="empty-state-icon" />
                                <p className="empty-state-title">Aucune filiale trouvée.</p>
                                <p className="empty-state-subtitle">Lancez une synchronisation pour importer les données.</p>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                {filiales.map((f, index) => {
                                    const variant = CARD_VARIANTS[index % CARD_VARIANTS.length];
                                    const label = getOrgLabel(f.org_unit_path);
                                    const depth = getOrgDepth(f.org_unit_path);

                                    return (
                                        <div
                                            key={f.id}
                                            className={`filiale-card filiale-card--${variant}`}
                                            onClick={() => navigate(`/filiale/${f.id}/devices`)}
                                        >
                                            <div className="filiale-card-glow"></div>

                                            <div className="filiale-card-icon">
                                                <Building2 className="filiale-card-icon-svg" />
                                            </div>

                                            <div className="filiale-card-content">
                                                <h3 className="filiale-card-title" title={f.org_unit_path}>
                                                    {label}
                                                </h3>
                                                <p className="filiale-card-path" title={f.org_unit_path}>
                                                    {f.org_unit_path}
                                                </p>
                                                {depth > 1 && (
                                                    <span className="filiale-depth-badge">Niveau {depth}</span>
                                                )}
                                            </div>

                                            <div className="filiale-card-footer">
                                                <span className="filiale-card-id">
                                                    <Server className="w-3 h-3" /> ID #{f.id}
                                                </span>
                                                <div className="filiale-see-btn">
                                                    Voir devices <ChevronRight className="w-3.5 h-3.5" />
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ListeFiliale;
