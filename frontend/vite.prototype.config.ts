import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import {fileURLToPath} from 'node:url';
export default defineConfig({
 plugins:[react()],base:'./',
 server:{host:'127.0.0.1',port:5174,strictPort:true,fs:{strict:true,allow:['.']}},
 build:{outDir:'dist/prototype-preview',rollupOptions:{input:fileURLToPath(new URL('./prototype/index.html',import.meta.url))}},
});
