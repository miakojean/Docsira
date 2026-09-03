import { defineStore } from "pinia";
import { computed, ref } from "vue";
import api from "../services/api";

export interface Customer{
  id?: string | number
  email: string
  first_name: string
  last_name: string
  username: string
  password: string
}

export const useAuthStore = defineStore('auth', () => {
  // state
  // =====
  // Ux

  const isLoading = ref<boolean>(false)

  const user = ref<Customer>({
    id:"",
    email: "",
    first_name: "",
    last_name: "",
    username: "",
    password: ""
  })

  const isAuthencticated = ref<boolean>(false);

  // Getters

  const setAutheticated = computed(()=>{return isAuthencticated.value = true})

  // Actions

  async function Registration(payload:Customer) {

    isLoading.value = true;

    try {

      const response = await api('/registration', 'POST', payload)

      if (response) {
        console.log("Utilisateur créé avec succès");
      }
    }
    catch (err: any) {
      throw err;
    }

    finally {
      isLoading.value = false;
    }
  }

  async function Login(payload:Extract<Customer, [us] >) {

    isLoading.value = true;

    try {

      const response = await api('/registration', 'POST', payload)

      if (response) {
        console.log("Utilisateur créé avec succès");
      }
    }
    catch (err: any) {
      throw err;
    }

    finally {
      isLoading.value = false;
    }
  }

  return {
    isLoading,
    user,
    isAuthencticated,

    // Getters
    setAutheticated,

    Registration,
    Login
  }
})
