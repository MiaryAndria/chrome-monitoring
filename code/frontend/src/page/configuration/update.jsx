import { useState,useEffect } from 'react';
import { updateConfiguration,getDetailConfiguration} from '../../fonction/configurationFonction';
import { useNavigate, useParams } from 'react-router-dom';
import { Pencil, ArrowLeft } from 'lucide-react';
import PageLayout from '../../components/PageLayout';
import '../../css/liste.css';
import '../../css/configuration.css';

function ConfigurationUpdate() {
    const [type, setType] = useState('');
    const [valeur, setValeur] = useState('');
    const [existedType,setExistedType]=useState('');
    const [existedValeur,setExistedValeur]=useState('');
    const navigate = useNavigate();
    const { id } = useParams();
    const getDetail = async(id)=>{
        try{
            const d = await getDetailConfiguration(id)
            setExistedType(d.type)
            setExistedValeur(d.valeur)
            console.log(d)
        }catch(e){
            console.log(e);
        }
    }
    
    const updConfiguration = async () => {
        try {
            await updateConfiguration(id, type, valeur);
            navigate('/liste/configuration');
        } catch (e) {
            console.log(e);
        }
    };

    useEffect(()=>{
        getDetail(id);
    },[id]);

    return (
        <PageLayout
            title="Modifier la configuration"
            subtitle={`Mise à jour de la configuration #${id}`}
            titleIcon={Pencil}
        >
            <div className="config-form-container">
                <div className="config-form">
                    <div className="config-form-title">
                        <div className="config-form-title-icon">
                            <Pencil className="w-5 h-5" />
                        </div>
                        Modifier configuration {existedType}
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Type</label>
                        <input
                            type="text"
                            className="config-form-input"
                            onChange={(e) => setType(e.target.value)}
                            placeholder={existedType}
                        />
                    </div>

                    <div className="config-form-group">
                        <label className="config-form-label">Valeur</label>
                        <input
                            type="text"
                            className="config-form-input"
                            onChange={(e) => setValeur(e.target.value)}
                            placeholder={existedValeur}
                        />
                    </div>

                    <div className="config-form-actions">
                        <button onClick={() => navigate('/liste/configuration')} className="config-btn config-btn-ghost">
                            <ArrowLeft className="w-4 h-4" /> Retour
                        </button>
                        <button onClick={updConfiguration} className="config-btn config-btn-primary">
                            <Pencil className="w-4 h-4" /> Mettre à jour
                        </button>
                    </div>
                </div>
            </div>
        </PageLayout>
    );
}

export default ConfigurationUpdate;
