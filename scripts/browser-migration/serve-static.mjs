#!/usr/bin/env node
import http from 'node:http';
import path from 'node:path';
import {readFile,stat,realpath} from 'node:fs/promises';
const root=await realpath(process.argv[2]??'/Users/kc/Documents/Codex/2026-11-05/valuation-platform-local/outputs/browser-portfolio/public');
const port=Number(process.argv[3]??5200);if(!Number.isInteger(port)||port<1024||port>65535)throw new Error('Invalid port');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.ico':'image/x-icon','.pdf':'application/pdf','.txt':'text/plain; charset=utf-8','.xml':'application/xml','.woff':'font/woff','.woff2':'font/woff2'};
const aliases={'/featured':'/featured.html','/project-pipeline':'/project-pipeline.html','/work':'/work.html','/contact':'/contact.html'};
async function file(name){const full=path.resolve(root,'.'+name);if(!full.startsWith(root+path.sep))return null;try{const real=await realpath(full);if(!real.startsWith(root+path.sep)||!(await stat(real)).isFile())return null;return {bytes:await readFile(real),type:mime[path.extname(real)]??'application/octet-stream'};}catch{return null;}}
http.createServer(async(req,res)=>{
 const send=(code,data,type='text/plain; charset=utf-8')=>{res.writeHead(code,{'Content-Type':type,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(req.method==='HEAD'?undefined:data);};
 if(!['GET','HEAD'].includes(req.method)){send(405,'Method not allowed');return;}
 let url;try{url=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);}catch{send(400,'Bad path');return;}
 if(url==='/__static_health'){send(200,JSON.stringify({status:'ok',mode:'static',backend:false}),'application/json');return;}
 if(url==='/valuation'){res.writeHead(301,{Location:'/valuation/'});res.end();return;}
 if(url.includes('\\')||url.split('/').some(x=>x==='..'||x.startsWith('.'))||url==='/api'||url.startsWith('/api/')){send(404,'Not found');return;}
 const resource=aliases[url]??(url.endsWith('/')?url+'index.html':url);
 let result=await file(resource);
 if(!result&&['/valuation/workspace','/valuation/workspace/'].includes(url))result=await file('/valuation/index.html');
 if(!result){send(404,'Not found');return;}send(200,result.bytes,result.type);
}).listen(port,'127.0.0.1',()=>console.log(`Static portfolio preview: http://127.0.0.1:${port}/valuation/`));
