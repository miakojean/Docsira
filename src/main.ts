import { createApp } from "vue";
import App from "./App.vue";
import { router } from './router/index.ts'
import { createPinia } from "pinia";



const app = createApp(App);

app.config.errorHandler = (err, _instance, info) => {
  console.error(`[Docsira Vue error] (${info}):`, err);
};

app.use(createPinia())
app.use(router)
app.mount("#app")
