import { defineConfig } from 'vite';
export default defineConfig(({mode}) => ({
  base: './',
  define: { __NOTEBOOK_REF__: JSON.stringify(process.env.VERCEL_GIT_COMMIT_SHA || 'codex/notebook-studio-20261014'), __EDITION__: JSON.stringify(mode === 'vercel' ? 'immersive' : 'guided') },
  build: { outDir: mode === 'hf' ? 'dist-hf' : mode === 'vercel' ? 'dist-vercel' : 'dist', chunkSizeWarningLimit: 750 },
  server: { host: '0.0.0.0' }
}));
