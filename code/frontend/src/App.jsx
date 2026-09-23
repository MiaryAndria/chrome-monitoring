import { Routes, Route } from 'react-router-dom'
import Connexion from './page/login'
import Dashboard from './page/dashboard'
import ListeDevice from './page/device/liste'
import ListeFiliale from './page/filiale/liste'
import ListeDeviceFiliale from './page/filiale/liste_device'
import DetailDevice from './page/device/detail_device'

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
        </Routes>
      </main>
  )
}

export default App