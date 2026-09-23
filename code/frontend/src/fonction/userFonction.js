import api_service from "../api/api_service"

export const Login = async(email,mdp)=>{
    try{
        const response = await api_service.post('/user/login',{
            email:email,
            mdp:mdp
        })
    } catch(e) {
        console.log(e);
        throw e; 
    }

};