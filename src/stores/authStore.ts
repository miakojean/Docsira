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
  account_type?: string;
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

  // Actions
  async function Registration(payload: Customer) {
    isLoading.value = true;
    message.value.errorMessage = "";
    try {
      const response = await api("/account/register/", "POST", payload, { requireAuth: false });
      if (!response.ok) {
        message.value.errorMessage = "Inscription impossible revoyez vos identifiants";
        return false;
      }
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
      const response = await api("/account/login/", "POST", payload, { requireAuth: false });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        message.value.errorMessage = errorData?.error || "Identifiants incorrects";
        return false;
      }

      const data = await response.json();
      if (data.access) {
        const store = await load("authStore.json", { autoSave: true });
        await store.set("auth_token", data.access);
        await store.set("refresh_token", data.refresh);
        await store.set("user", data.user);
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

  async function editProfile(payload: Customer) {
    isLoading.value = true;
    message.value.errorMessage = "";
    try {
      const response = await api('/account/me/', 'PUT', payload, { requireAuth: true });

      if (response.ok) {
        const updatedUser = await response.json();
        user.value = updatedUser;

        const store = await load("authStore.json", { autoSave: true });
        await store.set("user", updatedUser);
        await store.save();
        message.value.succesMessage = "Profile mis à jour";
        return true;
      }

      message.value.errorMessage = "Erreur serveur";
      return false;
    } catch (error) {
      message.value.errorMessage = "Erreur serveur";
      console.error(error);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function ChangePassword(payload: object) {
    isLoading.value = true;
    try {
      const response = await api('/account/change-password/', 'POST', { payload }, { requireAuth: true });
      if (response.ok) {
        message.value.succesMessage = "Mot de passe changé avec succès"
      } else {
        message.value.errorMessage = "Une erreur est survenue lors de la modification"
      }
    } catch {
      message.value.errorMessage = "Un soucis côté serveur est survenu"
    } finally {
      isLoading.value = false;
    }
  }

  async function Logout() {
    isLoading.value = true;
    message.value.errorMessage = "";

    try {
      const store = await load("authStore.json", { autoSave: true });
      const refreshToken = await store.get<string>("refresh_token");

      if (refreshToken) {
        await api(
          "/account/logout/",
          "POST",
          { refresh: refreshToken },
          { requireAuth: true },
        );
      }
    } catch (error) {
      console.error("Erreur lors de la déconnexion serveur :", error);
    } finally {
      const store = await load("authStore.json", { autoSave: true });
      await store.delete("auth_token");
      await store.delete("refresh_token");
      await store.delete("user");
      await store.save();

      isAuthenticated.value = false;
      user.value = {
        id: "",
        email: "",
        first_name: "",
        last_name: "",
        username: "",
        password: "",
      };
      await router.push("/login");
      isLoading.value = false;
    }
  }

  async function fetchUserProfile() {
    isLoading.value = true;
    try {
      const response = await api("/account/me/", "GET");
      if (response.ok) {
        user.value = await response.json();
        isAuthenticated.value = true;
      } else if (response.status === 401) {
        isAuthenticated.value = false;
        router.push("/login");
      }
    } catch (error) {
      message.value.errorMessage = "Erreur serveur";
      console.error(error);
    } finally {
      isLoading.value = false;
    }
  }

  const collaborators = ref<any[]>([]);

  async function fetchCollaborators() {
    isLoading.value = true;
    try {
      const response = await api("/account/collaborators/", "GET", undefined, { requireAuth: true });
      if (response.ok) {
        collaborators.value = await response.json();
        console.log("your collaborator", collaborators.value);
      } else {
        console.error("Failed to fetch collaborators");
      }
    } catch (error) {
      console.error(error);
    } finally {
      isLoading.value = false;
    }
  }

  async function addCollaborator(email: string) {
    isLoading.value = true;
    try {
      const response = await api("/account/collaborators/", 'POST', { email }, { requireAuth: true });
      if (response.ok) {
        message.value.succesMessage = "Invitation de collaboration envoyée";
        // Update collaborators list after successful add
        await fetchCollaborators();
        return true;
      } else {
        message.value.errorMessage = "Erreur lors de l'invitation: ce collaborateur a déjà été invité";
        return false;
      }
    } catch (error) {
      message.value.errorMessage = "Erreur serveur";
      console.error(error);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function removeCollaborator(email: string) {
    isLoading.value = true;
    try {
      const response = await api(`/account/collaborators/?email=${encodeURIComponent(email)}`, 'DELETE', undefined, { requireAuth: true });
      if (response.ok) {
        message.value.succesMessage = "Collaborateur retiré";
        await fetchCollaborators();
        return true;
      } else {
        const errorData = await response.json().catch(() => null);
        message.value.errorMessage = errorData?.error || "Erreur lors de la suppression";
        return false;
      }
    } catch (error) {
      message.value.errorMessage = "Erreur serveur";
      console.error(error);
      return false;
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
    collaborators,
    getIsAuthenticated,
    Registration,
    Login,
    Logout,
    editProfile,
    fetchUserProfile,
    addCollaborator,
    fetchCollaborators,
    ChangePassword
  };
});
