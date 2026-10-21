import { useState, useEffect } from "react";
import { getListeDevice } from "../../fonction/deviceFonction";
import { effectuerComparaisonSimple } from "../../fonction/comparaisonFonction";
function ComparaisonDouble() {
    const [deviceA, setDeviceA] = useState('');
    const [deviceB, setDeviceB] = useState('');
    const [listeDevice, setListeDevice] = useState([]);
    const [resulat ,setResultat]=useState(false)
    const [listeDeviceOpen, setListeDeviceOpen] = useState(false);

    const getDevice = async () => {
        try {
            const response = await getListeDevice()
            setListeDevice(response)
        } catch (e) {
            console.log(e)
        }
    }

    const comparer = async(a,b)=>{
        try{
            const response = await effectuerComparaisonSimple(a,b)
            setResultat(true)
        }catch(e){
            console.log(e)
        }
    }
    useEffect(() => {
        getDevice();
    }, [])

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (!e.target.closest('.relative')) {
                setListeDeviceOpen(false)
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    return (
        <div>
            <h2>Veuillez selectionnez les deux devices à comparer </h2>
            <h3>Device 1</h3>
            <div className="relative">
                <button
                    onClick={() => setListeDeviceOpen(v => !v)}
                    className={`topnav-link ${deviceActive ? 'topnav-link-active' : ''}`}
                >
                    <Laptop className="w-4 h-4" />
                    <span>Liste device </span>
                    <ChevronDown className="w-3 h-3" />
                </button>
                {listeDeviceOpen && (
                    <div className="config-dropdown">
                        {listeDeviceOpen.map((item) => {
                            return (
                                <div
                                    onClick={() => setListeDeviceOpen(false)}
                                    className="config-dropdown-item"
                                >
                                    <div className="w-4 h-4" />
                                    {item.model}
                                    <div className="w-4 h-4" />
                                    {item.serial_number}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            <h3>Device 1 autre version </h3>
            <div className="relative">
                <button
                    onClick={() => setListeDeviceOpen(v => !v)}
                    className={`topnav-link ${deviceActive ? 'topnav-link-active' : ''}`}
                >
                    <Laptop className="w-4 h-4" />
                    <span>Liste device </span>
                    <ChevronDown className="w-3 h-3" />
                </button>
                {listeDeviceOpen && (
                    <div className="config-dropdown">
                        {listeDeviceOpen.map((item) => {
                            return (
                                <div
                                    onClick={() => setListeDeviceOpen(false)}
                                    className="config-dropdown-item"
                                >
                                    <div className="w-4 h-4" />
                                    {item.model}
                                    <div className="w-4 h-4" />
                                    {item.serial_number}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
            <button onClick={()=>comparer(deviceA,deviceB)}>Comparer</button>
        </div>
    )

}
export default ComparaisonDouble