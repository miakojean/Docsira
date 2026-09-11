import { defineStore } from "pinia";
import { computed, ref } from "vue";
import api from "../services/api";
import { useRouter } from "vue-router";
// Importation du store Tauri pour la persistance
import { load } from '@tauri-apps/plugin-store';

export interface Customer {
  id?: string | number
  email: string
  first_name?: string
  last_name?: string
  username: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();

  const isLoading = ref<boolean>(false);
  const message = ref({ succesMessage: "", errorMessage:"" });
  const isAuthenticated = ref<boolean>(false);
  const user = ref<Customer>({
    id: "", email: "", first_name: "", last_name: "", username: "", password: ""
  });

  const getIsAuthenticated = computed(() => isAuthenticated.value);

  async function Registration(payload: Customer){
    isLoading.value = true;
    try {
      const response = await api('/account/register/', 'POST', payload);
      if (response.ok) {
        console.log("Utilisateur créé avec succès");
        router.push('/');
        return true;
      } else {
        message.value.errorMessage=""
      }
    } catch (err: any) {

      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function Login(payload: { username?: string; email?: string; password?: string }) {
    isLoading.value = true;
    message.value.errorMessage = "";

    try {
      const response = await api('/account/login/', 'POST', payload);

      if (response?.ok) {
        // 1. Extraction des données renvoyées par Django (incluant le JWT)
        const data = await response.json();

        // 2. Sauvegarde du jeton d'accès dans le système de fichiers natif chiffré
        if (data.access) {
          const store = await load('authStore.json', { autoSave: true });
          await store.set('auth_token', data.access);
        }

        isAuthenticated.value = true;
        message.value.succesMessage = "Connexion réussie";

        // Optionnel : Mettre à jour l'utilisateur local si Django renvoie ses infos
        if (data.user) user.value = data.user;

        router.push('/dashboard');
      } else {
        message.value.errorMessage = "Mot de passe ou nom d'utilisateur incorrect";
      }
    } catch (err: any) {
      message.value.errorMessage = "Erreur serveur, veuillez réessayer plus tard";
      console.error(err);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchUserProfile(){
    isLoading.value = true;
    try {
      const response = await api('/account/profile/', 'GET');
      if (response.ok) {
        const data = await response.json();
        user.value = data;
      }
    } catch (err: any) {
      message.value.errorMessage = "Erreur serveur";
    } finally {
      isLoading.value = false;
    }
  }

  return {
    router, isLoading, user, isAuthenticated, message,
    getIsAuthenticated, Registration, Login, fetchUserProfile
  }
});
