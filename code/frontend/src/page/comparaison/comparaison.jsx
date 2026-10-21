import { useState} from "react";
import { useNavigate } from "react-router-dom";
function Comparaison() {
    const navigate = useNavigate()
    return (
        <div>
            <h3>Voici liste et historique des comparaisons qui sont deja faites </h3>
            <h3>Vous pouvez selectionnez si dessous les options que vous voulez faire  </h3>
            <button onClick={()=>navigate('/comparaison/single')}>Comparaison un appareils de deux version differentes </button>
            <button onClick={()=>navigate('/comparaison/double')}>Comparaison deux appareils de meme types differentes </button>
        </div>
    )
}

export default Comparaison;
