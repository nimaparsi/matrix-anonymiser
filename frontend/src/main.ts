import { createSSRApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createSSRApp(App).use(router)
router.isReady().then(() => app.mount('#app'))
