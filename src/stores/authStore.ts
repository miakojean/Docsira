import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { load } from "@tauri-apps/plugin-store";
import { api } from "../services/api";

export interface Customer {
  id?: string | number;
  email: string;
  first_name?: string;
  last_name?: string;
  username: string;
  password: string;
}

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();
  const isLoading = ref(false);
  const message = ref({ succesMessage: "", errorMessage: "" });
  const isAuthenticated = ref(false);
  const user = ref<Customer>({
    id: "",
    email: "",
    first_name: "",
    last_name: "",
    username: "",
    password: "",
  });

  const getIsAuthenticated = computed(() => isAuthenticated.value);

  async function Registration(payload: Customer) {
    isLoading.value = true;
    try {
      const response = await api("/account/register/", "POST", payload);
      if (!response.ok) {
        message.value.errorMessage = "Inscription impossible";
        return false;
      }
      router.push("/");
      return true;
    } catch (error) {
      message.value.errorMessage = "Erreur serveur, veuillez réessayer plus tard";
      console.error(error);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function Login(payload: { username?: string; email?: string; password?: string }) {
    isLoading.value = true;
    message.value.errorMessage = "";
    try {
      const response = await api("/account/login/", "POST", payload);
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        message.value.errorMessage = errorData?.error || "Identifiants incorrects";
        return false;
      }

      const data = await response.json();
      if (data.access) {
        const store = await load("authStore.json", { autoSave: true });
        await store.set("auth_token", data.access);
      }
      isAuthenticated.value = true;
      message.value.succesMessage = "Connexion réussie";
      if (data.user) user.value = data.user;
      router.push("/dashboard");
      return true;
    } catch (error) {
      message.value.errorMessage = "Erreur serveur, veuillez réessayer plus tard";
      console.error(error);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchUserProfile() {
    isLoading.value = true;
    try {
      const response = await api("/account/me/", "GET");
      if (response.ok) user.value = await response.json();
    } catch (error) {
      message.value.errorMessage = "Erreur serveur";
      console.error(error);
    } finally {
      isLoading.value = false;
    }
  }

  return {
    router,
    isLoading,
    user,
    isAuthenticated,
    message,
    getIsAuthenticated,
    Registration,
    Login,
    fetchUserProfile,
  };
});
