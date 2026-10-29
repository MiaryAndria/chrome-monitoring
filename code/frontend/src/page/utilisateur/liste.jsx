import { useEffect, useState } from 'react';
import { Users, Check, Trash2, Archive } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import PageLayout from '../../components/PageLayout';
import GenericTable from '../../components/GenericTable';
import Pagination from '../../components/Pagination';
import TableSkeleton from '../../components/skeletons/TableSkeleton';
import usePaginatedData from '../../hooks/usePaginatedData';
import { getListeUtilisateurPage, getRoles, updateRoleUtilisateur, deleteUtilisateur } from '../../fonction/userFonction';
import '../../css/liste.css';
import '../../css/configuration.css';

function ListeUtilisateur() {
    const navigate = useNavigate();
    const [roles, setRoles] = useState([]);
    const [choix, setChoix] = useState({});
    const [savingId, setSavingId] = useState(null);
    const [error, setError] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [refresh, setRefresh] = useState(0);

    const { items: users, total, totalPages, loading } = usePaginatedData(
        getListeUtilisateurPage,
        currentPage,
        pageSize,
        { refresh }
    );

    useEffect(() => {
        getRoles()
            .then((listeRoles) => setRoles(listeRoles))
            .catch((e) => {
                console.log(e);
                setError("Impossible de charger les rôles.");
            });
    }, []);

    const validerRole = async (user, id_role) => {
        try {
            setSavingId(user.id);
            setError('');
            await updateRoleUtilisateur(user.id, id_role);
            setRefresh(r => r + 1);
        } catch (e) {
            console.log(e);
            setError("Impossible de modifier le rôle.");
        } finally {
            setSavingId(null);
        }
    };

    const supprimerUtilisateur = async (id) => {
        try {
            await deleteUtilisateur(id);
            setRefresh(r => r + 1);
        } catch (e) {
            console.log(e);
        }
    };

    const columns = [
        { header: 'Nom', className: 'w-[22%]', render: (u) => <span className="font-bold text-zinc-100">{u.nom}</span> },
        { header: 'Email', className: 'w-[28%]', render: (u) => <span className="text-zinc-300 font-mono text-xs">{u.email}</span> },
        {
            header: 'Rôle', className: 'w-[30%]', render: (u) => {
                const valeur = choix[u.id] ?? u.id_role;
                return (
                    <div className="flex items-center gap-2">
                        <select
                            value={valeur}
                            onChange={(e) => setChoix({ ...choix, [u.id]: Number(e.target.value) })}
                            className="bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-zinc-200 outline-none focus:border-cyan-500/60 cursor-pointer"
                        >
                            {roles.map((r) => (
                                <option key={r.id} value={r.id}>{r.role}</option>
                            ))}
                        </select>
                        {valeur !== u.id_role && (
                            <button
                                onClick={() => validerRole(u, valeur)}
                                disabled={savingId === u.id}
                                className="config-btn config-btn-primary"
                                style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}
                            >
                                <Check className="w-3.5 h-3.5" /> Valider
                            </button>
                        )}
                    </div>
                );
            }
        },
        {
            header: 'Actions', sticky: true, className: 'w-[20%] text-right', render: (u) => (
                <div className="config-table-actions">
                    <button
                        onClick={() => supprimerUtilisateur(u.id)}
                        className="config-btn config-btn-danger"
                        style={{ padding: '0.4rem 0.75rem', fontSize: '0.7rem' }}
                    >
                        <Trash2 className="w-3.5 h-3.5" /> Supprimer
                    </button>
                </div>
            )
        },
    ];

    return (
        <PageLayout
            title="Utilisateurs"
            subtitle="Gérer les comptes et leurs rôles"
            titleIcon={Users}
            headerRight={
                <button onClick={() => navigate('/liste/utilisateur/archive')} className="config-btn config-btn-primary">
                    <Archive className="w-4 h-4" /> Utilisateurs archivés
                </button>
            }
        >
            <div className="space-y-6">
                {error && (
                    <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 p-2.5 rounded-lg">
                        {error}
                    </div>
                )}

                {loading && users.length === 0 ? (
                    <TableSkeleton />
                ) : !users || users.length === 0 ? (
                    <div className="empty-state">
                        <Users className="empty-state-icon" />
                        <p className="empty-state-title">Aucun utilisateur trouvé.</p>
                        <p className="empty-state-subtitle">Aucun compte n'est enregistré.</p>
                    </div>
                ) : (
                    <>
                        <div className="section-header">
                            <div>
                                <h2 className="section-title">Liste des utilisateurs</h2>
                                <span className="section-count">{total} utilisateur(s)</span>
                            </div>
                        </div>
                        <GenericTable columns={columns} data={users} />

                        <Pagination
                            page={currentPage}
                            pageSize={pageSize}
                            totalPages={totalPages}
                            total={total}
                            loading={loading}
                            onPageChange={setCurrentPage}
                            onPageSizeChange={(size) => {
                                setPageSize(size);
                                setCurrentPage(1);
                            }}
                        />
                    </>
                )}
            </div>
        </PageLayout>
    );
}

export default ListeUtilisateur;
