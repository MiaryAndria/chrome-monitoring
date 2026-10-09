import { Routes, Route } from 'react-router-dom'
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
import archivedConfiguration from './page/configuration/archived'

function App() {
  return (
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Connexion />} />
          <Route path="/login" element={<Connexion />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/filiale" element={<ListeFiliale />} />
          <Route path="/filiale/:id_filiale/devices" element={<ListeDeviceFiliale />} />
          <Route path="/liste/device" element={<ListeDevice />} />
          <Route path="/device/:id" element={<DetailDevice />} />
          <Route path="/liste/event" element={<ListeEvent />} />
          <Route path="/imprimantes" element={<ListeImprimante />} />
          <Route path="/creer/configuration" element={<ConfigurationCreate />} />
          <Route path="/liste/configuration" element={<ConfigurationListe/>} />
          <Route path="/liste/configuration/archive" element={<archivedConfiguration/>} />
          <Route path="/update/configuration/:id" element={<ConfigurationUpdate/>} />
        </Routes>
      </main>
  )
}

export default App