import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import {fileURLToPath} from 'node:url';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const engine=process.env.VALUATION_ENGINE??'browser';
if(!['browser','python'].includes(engine))throw new Error('VALUATION_ENGINE must be browser or python');
const pythonEngine=engine==='python';
const apiTarget=process.env.VALUATION_LOCAL_API??'http://127.0.0.1:8000';
if(pythonEngine&&!/^http:\/\/127\.0\.0\.1:[0-9]{1,5}$/.test(apiTarget))throw new Error('Local API target must be numeric loopback HTTP');
export default defineConfig({
  define: {
    __VALUATION_BROWSER_ONLY__: JSON.stringify(!pythonEngine),
    __VALUATION_DATA_MANIFEST_SHA256__: JSON.stringify(createHash('sha256').update(readFileSync(fileURLToPath(new URL('./public/browser-data/manifest.json',import.meta.url)))).digest('hex')),
  },
  plugins: [react()],
  build: {rollupOptions: {input: {calculator:fileURLToPath(new URL('./index.html',import.meta.url)),workspace:fileURLToPath(new URL('./workspace/index.html',import.meta.url))}}},
  server: {
    host: '127.0.0.1', port: 5173, strictPort: true,
    proxy: pythonEngine?{ '/api': { target: apiTarget, timeout: 50000, proxyTimeout: 50000 } }:undefined,
    fs: { strict: true, allow: ['.'] },
  },
  preview: { host: '127.0.0.1', port: 4173, strictPort: true },
  test: { environment: 'jsdom', globals: true, setupFiles: ['./src/test-setup.ts'] },
});
