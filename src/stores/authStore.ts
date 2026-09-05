import { defineStore } from "pinia";
import { computed, ref } from "vue";
import api from "../services/api";
import { useRouter } from "vue-router";

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

  // State
  const isLoading = ref<boolean>(false);

  const message = ref({
    succesMessage: "",
    errorMessage:""
  })

  const isAuthenticated = ref<boolean>(false); // Typo corrigée

  const user = ref<Customer>({
    id: "",
    email: "",
    first_name: "",
    last_name: "",
    username: "",
    password: ""
  });

  // Getters
  // Correction de la fonction pour qu'elle renvoie simplement l'état
  const getIsAuthenticated = computed(() => isAuthenticated.value);

  // Actions
  async function Registration(payload: Customer){
    isLoading.value = true;
    try {
      // Le slash final est important pour Django
      const response = await api('account/register/', 'POST', payload);

      if (response.ok) {
        console.log("Utilisateur créé avec succès");
        router.push('/');
        return true;
      }
    } catch (err: any) {
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function Login(payload: Extract<Customer, "username" | "password" | "email">) {
    isLoading.value = true;
    try {
      // Assure-toi que cette route correspond exactement à celle de ton fichier urls.py Django
      const response = await api('/account/login/', 'POST', payload);

      if (response.ok) {
        console.log("Connexion réussie");
        isAuthenticated.value = true;
        message.value.succesMessage = "Connexion réussie";
        console.log(message.value.succesMessage)
      } else {
        message.value.errorMessage = "Mot de passe ou nom d'utilisateur incorrect";
        console.error(message.value.errorMessage)
      }

    } catch (err: any) {
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    router,
    // State
    isLoading,
    user,
    isAuthenticated,
    message,

    // Getters
    getIsAuthenticated,

    // Actions
    Registration,
    Login
  }
});
