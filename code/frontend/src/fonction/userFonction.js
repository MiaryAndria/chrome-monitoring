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

export const Register = async (nom, email, mdp) => {
  try {
    const response = await api_service.post("/user/signin", { nom, email, mdp });
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

export const getListeUtilisateurPage = async (params = {}) => {
  try {
    const response = await api_service.get("/user/liste/page", { params });
    return response.data;
  } catch (e) {
    console.log(e);
    return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
  }
};

export const getListeArchiverPage = async (params = {}) => {
  try {
    const response = await api_service.get("/user/liste/archiver/page", { params });
    return response.data;
  } catch (e) {
    console.log(e);
    return { items: [], total: 0, page: 1, page_size: params.page_size || 10, total_pages: 0 };
  }
};

export const getRoles = async () => {
  const response = await api_service.get("/user/role");
  return response.data;
};

export const updateRoleUtilisateur = async (id, id_role) => {
  const response = await api_service.put(`/user/${id}/role`, { id_role });
  return response.data;
};

export const deleteUtilisateur = async (id) => {
  try {
    return await api_service.post(`/user/${id}/delete`);
  } catch (e) {
    console.log(e);
    return null;
  }
};

export const restaurerUtilisateur = async (id) => {
  try {
    return await api_service.post(`/user/${id}/restaurer`);
  } catch (e) {
    console.log(e);
    return null;
  }
};
