import { useState, useEffect } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
    Activity, Building2, Laptop, Printer, Bell, BarChart3,
    Settings, ChevronDown, RotateCcw, RefreshCw, LogOut, Gauge,Copy,Check
} from 'lucide-react';
import { resetData } from '../fonction/importResetFonction';
import { Logout } from "../fonction/userFonction";
import { getNombreAlerte, getDixPremierAlerte } from '../fonction/alerteFonction';

export default function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();
    // const [isLightMode, setIsLightMode] = useState(false);
    const [configOpen, setConfigOpen] = useState(false);
    const [deviceOpen, setDeviceOpen] = useState(false);
    const [compareOpen, setCompareOpen] = useState(false);
    const [seuilOpen, setSeuilOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [alerteOpen, setAlerteOpen] = useState(false);
    const [alerteCount, setAlerteCount] = useState(0);
    const [alertes, setAlertes] = useState([]);
    const [copiedSN, setCopiedSN] = useState(null);

    // useEffect(() => {
    //     const storedTheme = localStorage.getItem('theme');
    //     if (storedTheme === 'light') {
    //         setIsLightMode(true);
    //         applyTheme('light');
    //     } else {
    //         setIsLightMode(false);
    //         applyTheme('dark');
    //     }
    // }, []);

    // Fermer les dropdowns au clic extérieur
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (!e.target.closest('.relative')) {
                setConfigOpen(false);
                setDeviceOpen(false);
                setAlerteOpen(false);
                setCompareOpen(false); // ← ajout
                setSeuilOpen(false);
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    useEffect(() => {
        const charger = () => getNombreAlerte().then((d) => setAlerteCount(d?.nombre ?? 0));
        charger();
        const timer = setInterval(charger, 60000);   // toutes les 60 s
        return () => clearInterval(timer);
    }, []);

    // const applyTheme = (theme) => {
    //     document.querySelectorAll('.device-layout').forEach(el => {
    //         el.setAttribute('data-theme', theme);
    //     });
    // };

    // const toggleTheme = () => {
    //     const newTheme = isLightMode ? 'dark' : 'light';
    //     setIsLightMode(!isLightMode);
    //     localStorage.setItem('theme', newTheme);
    //     applyTheme(newTheme);
    // };
    const voirTout = async () => {
        navigate('/alerte/device')
    }
    const handleLogout = async () => {
        await Logout();
        navigate("/login", { replace: true });
    };

    const resetAll = async () => {
        if (!window.confirm("Êtes-vous sûr de vouloir réinitialiser toutes les données ?")) return;
        try {
            setLoading(true);
            setMessage("Réinitialisation des données en cours...");
            await resetData();
            window.location.reload();
        } catch (e) {
            console.log(e);
        } finally {
            setLoading(false);
            setMessage("");
        }
    };

    const basculerAlertes = async () => {
        const ouvert = !alerteOpen;
        setAlerteOpen(ouvert);
        if (ouvert) {
            setAlertes(await getDixPremierAlerte());
        }
    };

    const handleCopySN = (serialNumber) => {
        if (!serialNumber) return;
        navigator.clipboard.writeText(serialNumber);
        setCopiedSN(serialNumber);
        setTimeout(() => setCopiedSN(null), 2000);
    };

    const navItems = [
        { path: '/filiale', label: 'Filiales', icon: Building2 },
        { path: '/liste/event', label: 'Événements', icon: Bell },
    ];

    const deviceItems = [
        { path: '/liste/device', label: 'Devices', icon: Laptop },
        { path: '/imprimantes', label: 'Imprimantes', icon: Printer },
    ];

    const configItems = [
        { path: '/liste/configuration', label: 'Liste configuration' },
        { path: '/creer/configuration', label: 'Créer configuration' },
        { path: '/liste/configuration/archive', label: 'Archive configuration' },
    ];

    const compareItems = [
        { path: '/comparaison/liste', label: 'Liste comparaison' },
        { path: '/comparaison/single', label: 'Simple comparaison' },
        { path: '/comparaison/double', label: 'Comparaison double' },
    ];

    const seuilItems = [
        { path: '/liste/seuil', label: 'Liste seuil' },
        { path: '/creer/seuil', label: 'Créer seuil' },
        { path: '/liste/seuil/archive', label: 'Archive seuil' },
    ]

    const configPaths = ['/liste/configuration', '/creer/configuration', '/liste/configuration/archive'];
    const comparePaths = ['/comparaison/single', '/comparaison/double'];
    const devicePaths = ['/liste/device', '/imprimantes'];
    const seuilPaths = ['/liste/seuil', '/creer/seuil', '/liste/seuil/archive'];
    const compareActive = comparePaths.some((c) => location.pathname.startsWith(c))
    const configActive = configPaths.some((p) => location.pathname.startsWith(p));
    const deviceActive = devicePaths.some((d) => location.pathname.startsWith(d));
    const seuilActive = seuilPaths.some((s) => location.pathname.startsWith(s));

    return (
        <>
            <div className="header-container glass-panel">
                <button onClick={() => navigate('/dashboard')} className="brand-button" title="Accueil">
                    <span className="brand-logo">
                        <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
                    </span>
                    <span className="brand-title">GT</span>
                </button>

                <nav className="topnav flex-1 justify-center">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) => isActive ? 'topnav-link topnav-link-active' : 'topnav-link'}
                            >
                                <Icon className="w-4 h-4" />
                                <span>{item.label}</span>
                            </NavLink>
                        );
                    })}

                    {/* Dropdown Matériel */}
                    <div className="relative">
                        <button
                            onClick={() => setDeviceOpen(v => !v)}
                            className={`topnav-link ${deviceActive ? 'topnav-link-active' : ''}`}
                        >
                            <Laptop className="w-4 h-4" />
                            <span>Matériel</span>
                            <ChevronDown className="w-3 h-3" />
                        </button>
                        {deviceOpen && (
                            <div className="config-dropdown">
                                {deviceItems.map((item) => {

                                    return (
                                        <NavLink
                                            key={item.path}
                                            to={item.path}
                                            onClick={() => setDeviceOpen(false)}
                                            className="config-dropdown-item"
                                        >
                                            <div className="w-4 h-4" />
                                            {item.label}
                                        </NavLink>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Dropdown Configuration */}
                    <div className="relative">
                        <button
                            onClick={() => setConfigOpen(v => !v)}
                            className={`topnav-link ${configActive ? 'topnav-link-active' : ''}`}
                        >
                            <Settings className="w-4 h-4" />
                            <span>Configuration</span>
                            <ChevronDown className="w-3 h-3" />
                        </button>
                        {configOpen && (
                            <div className="config-dropdown">
                                {configItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setConfigOpen(false)}
                                        className="config-dropdown-item"
                                    >
                                        {item.label}
                                    </NavLink>
                                ))}

                                <div className="config-dropdown-divider" />
                                <button
                                    onClick={() => { setConfigOpen(false); resetAll(); }}
                                    disabled={loading}
                                    className="config-dropdown-item config-dropdown-danger"
                                >
                                    <RotateCcw className="w-4 h-4" />
                                    Réinitialiser données
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Dropdown Seuil */}
                    <div className="relative">
                        <button
                            onClick={() => setSeuilOpen(v => !v)}
                            className={`topnav-link ${seuilActive ? 'topnav-link-active' : ''}`}
                        >
                            <Gauge className="w-4 h-4" />
                            <span>Seuil</span>
                            <ChevronDown className="w-3 h-3" />
                        </button>
                        {seuilOpen && (
                            <div className="config-dropdown">
                                {seuilItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setSeuilOpen(false)}
                                        className="config-dropdown-item"
                                    >
                                        {item.label}
                                    </NavLink>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Dropdown Comparaison */}
                    <div className="relative">
                        <button
                            onClick={() => setCompareOpen(v => !v)}
                            className={`topnav-link ${compareActive ? 'topnav-link-active' : ''}`}
                        >
                            <BarChart3 className="w-4 h-4" />
                            <span>Comparaison</span>
                            <ChevronDown className="w-3 h-3" />
                        </button>
                        {compareOpen && (
                            <div className="config-dropdown">
                                {compareItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setCompareOpen(false)}
                                        className="config-dropdown-item"
                                    >
                                        {item.label}
                                    </NavLink>
                                ))}
                            </div>
                        )}
                    </div>
                </nav>

                <div className="relative">
                    <button onClick={basculerAlertes} className="topnav-link relative" title="Alertes">
                        <Bell className="w-4 h-4" />
                        {alerteCount > 0 && (
                            <span className="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">
                                {alerteCount}
                            </span>
                        )}
                    </button>

                    {alerteOpen && (
                        <div className="config-dropdown alerte-dropdown">
                            <div className="alerte-list">
                                {alertes.length === 0 ? (
                                    <div className="alerte-empty">Aucune alerte</div>
                                ) : (
                                    alertes.map((a) => (
                                        <div key={a.id} className="alerte-item">
                                            <div className="alerte-item-top">
                                                <div className="flex items-center gap-1.5">
                                                    <span className="text-zinc-300 font-mono">{a.serial_number}</span>
                                                    <button
                                                        onClick={() => handleCopySN(a.serial_number)}
                                                        className="text-zinc-500 hover:text-cyan-400 transition-colors p-0.5 cursor-pointer"
                                                        title="Copier le numéro de série"
                                                    >
                                                        {copiedSN === a.serial_number ? (
                                                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                                                        ) : (
                                                            <Copy className="w-3.5 h-3.5" />
                                                        )}
                                                    </button>
                                                </div>
                                                <span className="alerte-type">{a.type?.replace('ALERTE_', '')}</span>
                                            </div>
                                            <div className="alerte-meta">
                                                {a.utilisateur_recent ?? 'utilisateur inconnu'} · {new Date(a.date).toLocaleString('fr-FR')}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                            <button className="alerte-footer" onClick={voirTout}>
                                Voir toutes les alertes
                            </button>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-3">
                    {/* <button
                        onClick={toggleTheme}
                        title="Basculer le thème"
                        className={`relative w-12 h-6 rounded border border-zinc-900 overflow-hidden shadow-[0_2px_5px_rgba(0,0,0,0.5)] flex items-center cursor-pointer ${isLightMode ? 'bg-zinc-300' : 'bg-zinc-800'}`}
                    >
                        <div className={`flex-1 h-full flex items-center justify-start pl-1.5 transition-colors ${isLightMode ? 'bg-zinc-200' : 'bg-zinc-700/50'}`}>
                            <span className={`text-[8px] font-black ${isLightMode ? 'text-zinc-600' : 'text-zinc-500'}`}>ON</span>
                        </div>
                        <div className={`flex-1 h-full flex items-center justify-end pr-1 transition-colors ${!isLightMode ? 'bg-zinc-900' : 'bg-zinc-300'}`}>
                            <span className={`text-[8px] font-black ${!isLightMode ? 'text-red-500/80' : 'text-zinc-500/50'}`}>OFF</span>
                        </div>
                        <div
                            className={`absolute top-0 bottom-0 w-[55%] transition-transform duration-200 ease-in-out border-l border-r border-black/10 ${isLightMode
                                ? 'translate-x-0 bg-gradient-to-r from-white to-zinc-200 shadow-[2px_0_3px_rgba(0,0,0,0.2)]'
                                : 'translate-x-[82%] bg-gradient-to-r from-zinc-600 to-zinc-800 shadow-[-2px_0_3px_rgba(0,0,0,0.4)]'
                                }`}
                        />
                    </button> */}

                    <button onClick={handleLogout} className="logout-btn" title="Se déconnecter">
                        <LogOut className="w-4 h-4" />
                        <span className="hidden sm:inline">Déconnexion</span>
                    </button>
                </div>
            </div>

            {loading && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center z-50 animate-fadeIn">
                    <div className="p-8 bg-zinc-900/90 border border-cyan-500/40 rounded-2xl shadow-[0_0_50px_rgba(6,182,212,0.3)] flex flex-col items-center max-w-sm text-center">
                        <div className="relative mb-6">
                            <div className="w-16 h-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin"></div>
                            <RefreshCw className="w-6 h-6 text-cyan-400 absolute inset-0 m-auto animate-pulse" />
                        </div>
                        <h3 className="text-lg font-bold text-zinc-100 mb-2">{message}</h3>
                        <p className="text-xs text-zinc-400 mb-4">Veuillez patienter pendant le traitement...</p>
                        <div className="w-full bg-zinc-800 rounded-full h-2.5 overflow-hidden border border-white/10 relative">
                            <div className="progress-bar-animated"></div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}