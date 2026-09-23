import { useEffect, useState } from "react";
import { useParams } from 'react-router-dom';
import { Server, Laptop, Network, User, Users, X, Copy, Check } from 'lucide-react';
import Sidebar from "../../components/Sidebar";
import Navbar from "../../components/Navbar";
import MouseSpotlight from "../../components/MouseSpotlight";
import { getDeviceDetail } from "../../fonction/deviceFonction";
import '../../css/liste.css';
import '../../css/filiale.css';
function DetailDevice() {
    const [copiedSN, setCopiedSN] = useState(null);
    const [device, setDevice] = useState(null);
    const { id } = useParams();
    const deviceDetail = async () => {
        try {
            const d = await getDeviceDetail(id)
            setDevice(d)
        } catch (e) {
            console.log(e)
        }
    }

    const handleCopySN = (serialNumber) => {
        if (!serialNumber) return;
        navigator.clipboard.writeText(serialNumber);
        setCopiedSN(serialNumber);
        setTimeout(() => setCopiedSN(null), 2000);
    };

    useEffect(() => {
        deviceDetail(id)
    }, [id])

    if (!device) return <div className="flex justify-center p-12">
        <span className="loading loading-infinity loading-lg text-cyan-500"></span>
    </div>
    return (
        <div>
            <button onClick={() => handleCopySN(device.serial_number)}
                className="text-zinc-500 hover:text-cyan-400 transition-colors p-0.5 cursor-pointer"
                title="Copier le numéro de série">
                {copiedSN === device.serial_number ? (
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                    <Copy className="w-3.5 h-3.5" />
                )}
            </button>

            <h3>Modèle : {device.modele}</h3>
            <h3>Statut : {device.status} </h3>
            <h3>Os Version : {device.chromeos_version} </h3>
            <h3>Chrome version : {device.chrome_version} </h3>
            <h3>Adresse Ip : {device.ip_adress}</h3>
            <h3>Mac_Adress : {device.mac_adress}</h3>
            <h3>Utilisateur assigné : {device.utilisateur_email}</h3>
            <h3>Utilisateur récent :</h3>
            <ul>
                {device.utilisateurs_recents.map((u, index) => (
                    <li key={index}>{u}</li>
                ))}
            </ul>
        </div>
    )

}
export default DetailDevice;