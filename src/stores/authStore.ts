import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { api, clearAuthSession, getAuthStore } from "../services/api";

export interface Customer {
  id?: string | number;
  email: string;
  first_name?: string;
  last_name?: string;
  username: string;
  password: string;
  account_type?: string;
  has_changed_password?: boolean;
}

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();
  const isLoading = ref(false);
  const message = ref({ succesMessage: "", errorMessage: "" });
  const isAuthenticated = ref(false);
  const isHydrated = ref(false);
  const user = ref<Customer>({
    id: "",
    email: "",
    first_name: "",
    last_name: "",
    username: "",
    password: "",
  });

  const getIsAuthenticated = computed(() => isAuthenticated.value);

  function resetLocalAuthState() {
    isAuthenticated.value = false;
    user.value = {
      id: "",
      email: "",
      first_name: "",
      last_name: "",
      username: "",
      password: "",
    };
  }

  async function hydrateSession() {
    try {
      const store = await getAuthStore();
      const token = await store.get<string>("auth_token");
      const savedUser = await store.get<Customer>("user");
      if (token) {
        isAuthenticated.value = true;
        if (savedUser) user.value = savedUser;
      } else {
        resetLocalAuthState();
      }
    } catch {
      resetLocalAuthState();
    } finally {
      isHydrated.value = true;
    }
  }

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

      const data = await response.json().catch(() => null);
      if (!data?.access) {
        message.value.errorMessage = "Réponse de connexion invalide (jeton manquant)";
        return false;
      }

      const store = await getAuthStore();
      await store.set("auth_token", data.access);
      if (data.refresh) {
        await store.set("refresh_token", data.refresh);
      }
      if (data.user) {
        await store.set("user", data.user);
        user.value = data.user;
      }
      await store.save();

      isAuthenticated.value = true;
      isHydrated.value = true;
      message.value.succesMessage = "Connexion réussie";
      const redirect = router.currentRoute.value.query.redirect;
      const target = typeof redirect === "string" && redirect.startsWith("/") ? redirect : "/dashboard";
      await router.push(target);
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

        const store = await getAuthStore();
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

  async function ChangePassword(payload: {
    old_password: string;
    new_password: string;
    confirm_password: string;
  }) {
    isLoading.value = true;
    try {
      const response = await api('/account/change-password/', 'POST', payload, { requireAuth: true });
      if (response.ok) {
        message.value.succesMessage = "Mot de passe changé avec succès";
        return true;
      }

      const errorData = await response.json().catch(() => null);
      const backendError = errorData?.error;
      message.value.errorMessage = Array.isArray(backendError)
        ? backendError.join(' ')
        : backendError || "Une erreur est survenue lors de la modification";
      return false;
    } catch (error) {
      message.value.errorMessage = "Un soucis côté serveur est survenu";
      console.error(error);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function Logout() {
    isLoading.value = true;
    message.value.errorMessage = "";

    try {
      const store = await getAuthStore();
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
      await clearAuthSession();
      resetLocalAuthState();
      await router.push("/login");
      isLoading.value = false;
    }
  }

  async function fetchUserProfile() {
    isLoading.value = true;
    try {
      const response = await api("/account/me/", "GET");
      if (response.ok) {
        const profile = await response.json();
        user.value = profile;
        isAuthenticated.value = true;
        const store = await getAuthStore();
        await store.set("user", profile);
        await store.save();
      } else if (response.status === 401) {
        await clearAuthSession();
        resetLocalAuthState();
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
      const allItems: any[] = [];
      let page = 1;
      for (;;) {
        const response = await api(`/account/collaborators/?page=${page}`, "GET", undefined, { requireAuth: true });
        if (!response.ok) {
          console.error("Failed to fetch collaborators");
          return;
        }
        const data = await response.json();
        if (Array.isArray(data)) {
          collaborators.value = data;
          return;
        }
        allItems.push(...(data.results ?? []));
        if (!data.next) {
          collaborators.value = allItems;
          return;
        }
        page += 1;
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

  function clearMessages() {
    message.value.errorMessage = "";
    message.value.succesMessage = "";
  }

  return {
    router,
    isLoading,
    user,
    isAuthenticated,
    isHydrated,
    message,
    collaborators,
    getIsAuthenticated,
    hydrateSession,
    resetLocalAuthState,
    Registration,
    Login,
    Logout,
    editProfile,
    fetchUserProfile,
    addCollaborator,
    fetchCollaborators,
    removeCollaborator,
    ChangePassword,
    clearMessages
  };
});
