#!/usr/bin/env node
// Verify a release artifact offline and optionally probe its loopback static host.
import path from 'node:path';
import {readFile,readdir,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {hasRecognizableSecret} from './public-asset-checks.mjs';
const output=path.resolve(process.argv[2]??'/Users/kc/Documents/Codex/2026-11-05/valuation-platform-local/outputs/browser-portfolio');
const origin=process.argv[3];if(origin&&!/^http:\/\/127\.0\.0\.1:\d+$/.test(origin))throw new Error('Only loopback validation is supported');
const root=path.join(output,'public');
const manifest=JSON.parse(await readFile(path.join(output,'release-manifest.json'),'utf8'));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const names=new Set(manifest.files.map(f=>f.path));
const reject=(message)=>{throw new Error(message);};
async function actualFiles(dir,rel=''){let out=[];for(const ent of await readdir(dir,{withFileTypes:true})){const p=path.posix.join(rel,ent.name);if(ent.isSymbolicLink())reject('Symlink publication: '+p);if(ent.isDirectory())out.push(...await actualFiles(path.join(dir,ent.name),p));else out.push(p);}return out;}
const actual=await actualFiles(root);if(actual.length!==names.size||actual.some(p=>!names.has(p)))reject('Unmanifested/missing public files');
let references=0;
for(const file of manifest.files){
 const bytes=await readFile(path.join(root,file.path));if(bytes.length!==file.bytes||digest(bytes)!==file.sha256)reject('Manifest mismatch: '+file.path);
 if(/(?:^|\/)(?:fixtures|node_modules|functions|\.git|\.env)(?:\/|$)|\.map$|(?:firebase|netlify)\.json$/.test(file.path))reject('Forbidden public file: '+file.path);
 if(!/\.(?:html|js|mjs|css|json)$/.test(file.path))continue;
 const text=bytes.toString('utf8');
 if(/https?:\/\/[^\s"'<>]*(?:\.run\.app|\.cloudfunctions\.net|\.firebaseio\.com|127\.0\.0\.1|localhost)(?::\d+)?/i.test(text))reject('Cloud/loopback backend URL in public artifact: '+file.path);
 if(hasRecognizableSecret(text))reject('Recognizable secret material: '+file.path);
 const refs=file.path.endsWith('.html')?[...text.matchAll(/(?:src|href)=["']([^"']+)["']/g)].map(m=>m[1]):file.path.endsWith('.css')?[...text.matchAll(/url\(["']?([^\s)'";]+)["']?\)/g)].map(m=>m[1]):/\.(?:js|mjs)$/.test(file.path)?[...text.matchAll(/["']((?:\.?\.?\/)[^"'\s]+\.(?:js|mjs|css)(?:\?[^"'\s]*)?)["']/g)].map(m=>m[1]):[];
 for(const ref of refs){
  if(/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(ref))continue;
  let target=new URL(ref,'https://static.invalid/'+file.path).pathname;target=decodeURIComponent(target).slice(1);
  if(target.endsWith('/'))target+='index.html';
  if(!names.has(target))reject(`Missing reference in ${file.path}: ${ref}`);references++;
 }
}
const redirects=await readFile(path.join(root,'_redirects'),'utf8');
if(/\/api|https?:|\/valuation\/\*\s+\/valuation\/index\.html/.test(redirects))reject('Backend rewrite or unsafe broad extension fallback');
if(origin){
 const cases=[['/',200],['/featured',200],['/contact.html',200],['/resume.pdf',200],['/valuation',301],['/valuation/',200],['/valuation/workspace/',200],['/valuation/calculator.html',200],['/valuation/not-found.js',404],['/valuation/not-found.json',404],['/valuation/assets/not-found.css',404],['/valuation/browser-data/not-found.json',404],['/api/health',404],['/not-found',404],['/release-manifest.json',404],['/.git/config',404]];
 for(const [url,status]of cases){const response=await fetch(origin+url,{redirect:'manual'});if(response.status!==status)reject(`${url}: expected ${status}, got ${response.status}`);if(status===404&&response.headers.get('content-type')?.includes('text/html'))reject('HTML response for missing route '+url);}
 for(const file of manifest.files.filter(f=>/\.(?:js|mjs|css|json)$/.test(f.path))){const response=await fetch(origin+'/'+file.path);if(!response.ok||digest(Buffer.from(await response.arrayBuffer()))!==file.sha256)reject('Hosted asset mismatch '+file.path);const type=response.headers.get('content-type')??'';if(/\.(?:js|mjs)$/.test(file.path)&&!type.startsWith('text/javascript'))reject('JavaScript MIME '+file.path);}
}
console.log(JSON.stringify({status:'PASS',files:names.size,localReferences:references,loopbackRoutes:origin?'PASS':'not requested',backend:'none',hostingAccess:'not checked'}));
