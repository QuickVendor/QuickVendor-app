import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    dedupe: ['react', 'react-dom', 'react-router', 'react-router-dom']
  },
  optimizeDeps: {
    include: ['react-router-dom', 'react-router'],
    exclude: ['lucide-react'],
  },
  build: {
    commonjsOptions: {
      include: [/react-router/, /node_modules/]
    }
  },
});
