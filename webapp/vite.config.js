import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'


export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')
    console.log(env.VITE_WEBAPP_URL)
    return {
        plugins: [react(), tailwindcss()],
        server: {
            allowedHosts: [env.VITE_WEBAPP_URL]
        }
    }
})