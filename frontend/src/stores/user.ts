import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi, type LoginData } from "@/api";
import { ElMessage } from "element-plus";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem("token") || "");
  const username = ref<string>(localStorage.getItem("username") || "");

  const isLoggedIn = computed(() => !!token.value);

  async function register(
    user: string,
    password: string
  ): Promise<boolean> {
    try {
      const { data: res } = await authApi.register(user, password);
      if (res.code === 0) {
        return true;
      } else {
        ElMessage.error(res.message);
        return false;
      }
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || "注册失败");
      return false;
    }
  }

  async function login(
    user: string,
    password: string
  ): Promise<boolean> {
    try {
      const { data: res } = await authApi.login(user, password);
      if (res.code === 0) {
        token.value = res.data.access_token;
        username.value = user;
        localStorage.setItem("token", res.data.access_token);
        localStorage.setItem("username", user);
        return true;
      } else {
        ElMessage.error(res.message);
        return false;
      }
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || "Login failed");
      return false;
    }
  }

  function logout() {
    token.value = "";
    username.value = "";
    localStorage.removeItem("token");
    localStorage.removeItem("username");
  }

  return {
    token,
    username,
    isLoggedIn,
    register,
    login,
    logout,
  };
});
