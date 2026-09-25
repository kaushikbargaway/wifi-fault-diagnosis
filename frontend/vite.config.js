import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // Inline PostCSS config — prevents Vite from searching for postcss.config.js
  // and avoids the BOM-related JSON parsing error on Windows.
  css: {
    postcss: {
      plugins: [],
    },
  },

  server: {
    port: 5173,
    proxy: {
      // Forward /api/* requests to the FastAPI backend during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
