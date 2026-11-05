#!/usr/bin/env node
// Assembles a static review artifact; never edits either source checkout.
import {readFile,writeFile,mkdir,readdir,stat,realpath} from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const args=process.argv.slice(2);
const production=args.includes('--production');
const option=(name,fallback)=>{const i=args.indexOf(name);return i<0?fallback:args[i+1];};
const portfolio=path.resolve(option('--portfolio','/Users/kc/Projects/Website/V3/kartikchaturvedi.com'));
const build=path.resolve(option('--build',path.join(repo,'frontend/dist-browser')));
const output=path.resolve(option('--output','/Users/kc/Documents/Codex/2026-11-05/valuation-platform-local/outputs/browser-portfolio'));
for(const root of [repo,portfolio])if(output===root||output.startsWith(root+path.sep))throw new Error('Artifact must be outside both source repositories');
await stat(path.join(build,'workspace/index.html'));
await mkdir(output,{recursive:false}); // Refuse to replace an earlier release.
const publicDir=path.join(output,'public');await mkdir(publicDir);
const records=[];
const hash=data=>createHash('sha256').update(data).digest('hex');
async function publish(source,destination){
 const resolved=await realpath(source);if(resolved!==path.resolve(source))throw new Error(`Symlink input forbidden: ${source}`);
 const bytes=await readFile(source);const target=path.join(publicDir,destination);
 await mkdir(path.dirname(target),{recursive:true});await writeFile(target,bytes,{flag:'wx'});
 records.push({path:destination,sha256:hash(bytes),bytes:bytes.length,source});
}
const allowed=['index.html','featured.html','project-pipeline.html','work.html','contact.html','style.css','profile.jpg','resume.pdf','robots.txt','sitemap.xml'];
for(const file of allowed)await publish(path.join(portfolio,file),file);
async function walk(root,rel=''){
 for(const entry of await readdir(path.join(root,rel),{withFileTypes:true})){
  const name=path.posix.join(rel,entry.name);
  if(entry.isSymbolicLink()||entry.name.startsWith('.'))throw new Error(`Unsafe build input: ${name}`);
  if(entry.isDirectory()){if(['node_modules','functions','.netlify'].includes(entry.name))throw new Error(`Forbidden build directory: ${name}`);await walk(root,name);}
  else if(entry.isFile()){
   if(name.endsWith('.map')||!(/\.(html|js|mjs|css|json|png|jpg|jpeg|webp|svg|ico|woff2?)$/i.test(name)))throw new Error(`Non-public build file: ${name}`);
   const target=name==='workspace/index.html'?'valuation/index.html':name==='index.html'?'valuation/calculator.html':`valuation/${name}`;
   await publish(path.join(root,name),target);
  }
 }
}
await walk(build);
const redirects='/valuation /valuation/ 301\n/featured /featured.html 200\n/project-pipeline /project-pipeline.html 200\n/work /work.html 200\n/contact /contact.html 200\n/valuation/workspace /valuation/index.html 200\n/valuation/workspace/ /valuation/index.html 200\n';
// Exact missing resources must never become successful HTML; no global SPA fallback.
const headers='/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n'+(production?'  Cache-Control: public, max-age=0, must-revalidate\n':'  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n')+'  Content-Security-Policy: default-src \'self\'; connect-src \'self\'; worker-src \'self\'; img-src \'self\' data:; style-src \'self\' \'unsafe-inline\' https://fonts.googleapis.com; font-src \'self\' https://fonts.gstatic.com; script-src \'self\'; frame-ancestors \'none\'; base-uri \'none\'; object-src \'none\'\n/valuation/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n';
for(const [name,data]of Object.entries({'_redirects':redirects,'_headers':headers,'404.html':'<!doctype html><html lang="en"><meta charset="utf-8"><title>Not found</title><h1>Not found</h1></html>\n'})){
 await writeFile(path.join(publicDir,name),data,{flag:'wx'});records.push({path:name,sha256:hash(data),bytes:Buffer.byteLength(data),source:'generated'});
}
const commit=cwd=>execFileSync('git',['rev-parse','HEAD'],{cwd,encoding:'utf8'}).trim();
const status=cwd=>execFileSync('git',['status','--porcelain'],{cwd,encoding:'utf8'}).trim();
await writeFile(path.join(output,'release-manifest.json'),JSON.stringify({schema:'browser-portfolio-release/v1',createdAt:new Date().toISOString(),sources:{valuation:{directory:repo,commit:commit(repo),workingTreeStatus:status(repo)},portfolio:{directory:portfolio,commit:commit(portfolio),workingTreeStatus:status(portfolio)}},files:records.sort((a,b)=>a.path.localeCompare(b.path)),publication:{directory:'public',backend:'none',production,notes:production?'Production artifact; publication requires user authorization.':'Draft review artifact. Does not establish Netlify account access or private protection.'}},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output,publicDir,files:records.length}));
