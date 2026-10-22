
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

const isGitHubPages = process.env.GITHUB_PAGES === 'true'

export default defineConfig({
    plugins: [react()],

    base: isGitHubPages ? '/intern_project/' : '/static/react/',

    build: {
        outDir: isGitHubPages
            ? path.resolve(__dirname, 'dist')
            : path.resolve(__dirname, '../backend/static/react'),
        emptyOutDir: true,
    },
})
