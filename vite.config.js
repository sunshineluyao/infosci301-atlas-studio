import { defineConfig } from 'vite';
export default defineConfig(({mode}) => ({
  base: './',
  define: { __EDITION__: JSON.stringify(mode === 'vercel' ? 'immersive' : 'guided') },
  build: { outDir: mode === 'hf' ? 'dist-hf' : mode === 'vercel' ? 'dist-vercel' : 'dist', chunkSizeWarningLimit: 750 },
  server: { host: '0.0.0.0' }
}));
