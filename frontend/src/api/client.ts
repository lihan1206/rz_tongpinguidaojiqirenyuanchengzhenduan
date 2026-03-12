import axios from "axios";
import { message, notification } from "antd";

const apiBase = import.meta.env.VITE_API_BASE || "/api";

export const client = axios.create({
  baseURL: apiBase,
  timeout: 15000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status;
    const detail = error?.response?.data?.detail;

    if (status === 401) {
      localStorage.removeItem("access_token");
      message.error(detail ?? "登录已失效，请重新登录");
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (status === 403) {
      notification.warning({
        message: "权限不足",
        description: detail ?? "当前账号没有权限执行该操作",
        placement: "topRight",
      });
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);
