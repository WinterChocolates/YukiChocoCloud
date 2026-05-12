import axios from "axios";

const http = axios.create({
  baseURL: "/api",
  timeout: 30000,
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface LoginData {
  access_token: string;
  token_type: string;
}

export interface FileInfo {
  id: number;
  name: string;
  is_dir: boolean;
  size: number;
  created_at: string;
}

export interface StorageInfo {
  used: number;
  total: number;
}

export interface ShareInfo {
  id: number;
  token: string;
  file_id: number;
  has_password: boolean;
  expire_at: string | null;
  created_at: string;
}

export interface PublicShareInfo {
  file_name: string;
  file_size: number;
  is_dir: boolean;
}

export const authApi = {
  register(username: string, password: string) {
    return http.post<ApiResponse>("/auth/register", { username, password });
  },
  login(username: string, password: string) {
    return http.post<ApiResponse<LoginData>>("/auth/login", { username, password });
  },
};

export const filesApi = {
  list(parentId?: number) {
    return http.get<ApiResponse<FileInfo[]>>("/files", { params: { parent_id: parentId } });
  },
  createFolder(name: string, parentId?: number) {
    return http.post<ApiResponse<FileInfo>>("/files", { name, parent_id: parentId });
  },
  remove(id: number) {
    return http.delete<ApiResponse<FileInfo>>(`/files/${id}`);
  },
  upload(file: File, parentId?: number) {
    const formData = new FormData();
    formData.append("file", file);
    if (parentId !== undefined) {
      formData.append("parent_id", String(parentId));
    }
    return http.post<ApiResponse<FileInfo>>("/upload", formData);
  },
  download(fileId: number) {
    return http.get(`/download/${fileId}`, {
      responseType: "blob",
    });
  },
  preview(fileId: number) {
    return http.get(`/preview/${fileId}`, {
      responseType: "blob",
    });
  },
  getStorageInfo() {
    return http.get<ApiResponse<StorageInfo>>("/files/storage");
  },
};

export const sharesApi = {
  create(fileId: number, password?: string, expireAt?: string) {
    return http.post<ApiResponse<ShareInfo>>("/shares", {
      file_id: fileId,
      password: password || undefined,
      expire_at: expireAt || undefined,
    });
  },
  listByFile(fileId: number) {
    return http.get<ApiResponse<ShareInfo[]>>(`/files/${fileId}/shares`);
  },
  remove(shareId: number) {
    return http.delete<ApiResponse>(`/shares/${shareId}`);
  },
  access(token: string, password?: string) {
    return http.post<ApiResponse<PublicShareInfo>>(
      `/public/share/${token}`,
      { password: password || undefined }
    );
  },
  download(token: string, password?: string) {
    return http.post(
      `/public/share/${token}/download`,
      { password: password || undefined },
      { responseType: "blob" }
    );
  },
};

export default http;
