import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import router from './router'
import App from './App.vue'
import Icon from './components/ui/Icon.vue'
import './style.css'

const app = createApp(App)

app.component('Icon', Icon)

app.use(createPinia())
app.use(router)
app.use(VueQueryPlugin, {
 queryClientConfig: {
 defaultOptions: {
 queries: {
 staleTime: 1000 * 60 * 5, // 5 minutes
 retry: 1,
 },
 },
 },
})

app.mount('#app')
