import { useState, useEffect } from 'react';
import { updateConfiguration } from '../../fonction/configurationFonction';
import { useNavigate, useParams } from 'react-router-dom';
function ConfigurationUpdate() {
    const [type, setType] = useState('');
    const [valeur, setValeur] = useState('');
    const [date, setDate] = useState('');
    const navigate = useNavigate()
    const {id}= useParams()

    const updConfiguration = async () => {
        try {
            await updateConfiguration(id,type,valeur,date)
            navigate('/liste/configuration')
        } catch (e) {
            console.log(e)
        }
    }

    return (
        <div>
            <input type='text'onChange={(e)=>setType(e.target.value)}placeholder='Entrer type configuration'></input>
            <input type='text'onChange={(e)=>setValeur(e.target.value)}placeholder='Entrer valeur'></input>
            <button onClick={updConfiguration}>Mettre à jour </button>
        </div>
    )
}

export default ConfigurationUpdate;
