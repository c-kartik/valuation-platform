import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import {fileURLToPath} from 'node:url';

const apiTarget=process.env.VALUATION_LOCAL_API??'http://127.0.0.1:8000';
if(!/^http:\/\/127\.0\.0\.1:[0-9]{1,5}$/.test(apiTarget))throw new Error('Local API target must be numeric loopback HTTP');
export default defineConfig({
  plugins: [react()],
  build: {rollupOptions: {input: {calculator:fileURLToPath(new URL('./index.html',import.meta.url)),workspace:fileURLToPath(new URL('./workspace/index.html',import.meta.url))}}},
  server: {
    host: '127.0.0.1', port: 5173, strictPort: true,
    proxy: { '/api': { target: apiTarget, timeout: 50000, proxyTimeout: 50000 } },
    fs: { strict: true, allow: ['.'] },
  },
  preview: { host: '127.0.0.1', port: 4173, strictPort: true },
  test: { environment: 'jsdom', globals: true, setupFiles: ['./src/test-setup.ts'] },
});
