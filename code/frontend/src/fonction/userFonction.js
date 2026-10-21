import api_service from "../api/api_service";

export const Login = async (email, mdp) => {
  try {
    const response = await api_service.post("/user/login", { email, mdp });
    return response.data;
  } catch (e) {
    console.log(e);
    throw e;
  }
};

export const Logout = async () => {
  await api_service.post("/user/logout");
};

export const GetMe = async () => {
  const response = await api_service.get("/user/me");
  return response.data;
};