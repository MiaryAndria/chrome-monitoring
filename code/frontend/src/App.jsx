import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import PublicRoute from './components/PublicRoute'
import Connexion from './page/login'
import Dashboard from './page/dashboard'
import ListeDevice from './page/device/liste'
import ListeFiliale from './page/filiale/liste'
import ListeDeviceFiliale from './page/filiale/liste_device'
import DetailDevice from './page/device/detail_device'
import ListeEvent from './page/event/liste'
import ListeImprimante from './page/imprimante/liste'
import ConfigurationCreate from './page/configuration/create'
import ConfigurationListe from './page/configuration/liste'
import ConfigurationUpdate from './page/configuration/update'
import ArchivedConfiguration from './page/configuration/archived'
import SeuilCreate from './page/seuil/create'
import SeuilListe from './page/seuil/liste'
import SeuilUpdate from './page/seuil/update'
import ArchivedSeuil from './page/seuil/archived'
import DetailImprimante from './page/imprimante/detailImprimante'
import ComparaisonSingle from './page/comparaison/comparaison_single'
import ComparaisonDouble from './page/comparaison/comparaison_double'
import Comparaison from './page/comparaison/comparaison'
import ListeDeviceAlerte from './page/alerte/device/liste'
import ListeDeviceAlerteResolue from './page/alerte/device/resolue'
function App() {
  return (
    <main className="main-content">
      <Routes>
        {/* Routes publiques : redirigent vers /dashboard si déjà connecté */}
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<Connexion />} />
        </Route>

        {/* Routes privées : redirigent vers /login si non connecté */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/filiale" element={<ListeFiliale />} />
          <Route path="/filiale/:id_filiale/devices" element={<ListeDeviceFiliale />} />
          <Route path="/liste/device" element={<ListeDevice />} />
          <Route path="/device/:id" element={<DetailDevice />} />
          <Route path="/liste/event" element={<ListeEvent />} />
          <Route path="/imprimantes" element={<ListeImprimante />} />
          <Route path="/imprimante/:id" element={<DetailImprimante />} />
          <Route path="/creer/configuration" element={<ConfigurationCreate />} />
          <Route path="/liste/configuration" element={<ConfigurationListe />} />
          <Route path="/liste/configuration/archive" element={<ArchivedConfiguration />} />
          <Route path="/update/configuration/:id" element={<ConfigurationUpdate />} />
          <Route path="/creer/seuil" element={<SeuilCreate />} />
          <Route path="/liste/seuil" element={<SeuilListe />} />
          <Route path="/liste/seuil/archive" element={<ArchivedSeuil />} />
          <Route path="/update/seuil/:id" element={<SeuilUpdate />} />
          <Route path="/comparaison/liste" element={<Comparaison/>} />
          <Route path="/comparaison/single" element={<ComparaisonSingle />} />
          <Route path="/comparaison/double" element={<ComparaisonDouble />} />
          <Route path="/alerte/device" element={<ListeDeviceAlerte />} />
          <Route path="/alerte/device/resolue" element={<ListeDeviceAlerteResolue />} />
        </Route>
        
        {/* "/" et toute URL inconnue → login (la PublicRoute renverra vers /dashboard si connecté) */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </main>
  )
}

export default App