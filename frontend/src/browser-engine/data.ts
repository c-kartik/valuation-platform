import {clone,type Doc} from './decimal';
import type {EngineData} from './case';
declare const __VALUATION_DATA_MANIFEST_SHA256__:string;
const base=()=>new URL(((import.meta as any).env?.BASE_URL??'/')+'browser-data/',location.origin);
const hex=(value:ArrayBuffer)=>Array.from(new Uint8Array(value)).map(v=>v.toString(16).padStart(2,'0')).join('');
async function verified(url:URL,pin:string){
 const response=await fetch(url,{credentials:'omit',cache:'no-cache'});if(!response.ok)throw new Error('Prepared dataset unavailable');
 const bytes=await response.arrayBuffer();if(bytes.byteLength>2*1024*1024)throw new Error('Prepared dataset exceeds size limit');
 const digest=hex(await crypto.subtle.digest('SHA-256',bytes));if(digest!==pin)throw new Error('Prepared dataset integrity mismatch');return JSON.parse(new TextDecoder().decode(bytes));
}
let manifest:Promise<Doc>|undefined;const assets=new Map<string,Promise<any>>();
function getManifest(){return manifest??=(verified(new URL('manifest.json',base()),__VALUATION_DATA_MANIFEST_SHA256__).catch(e=>{manifest=undefined;throw e;}));}
async function asset(file:string){
 if(!assets.has(file))assets.set(file,(async()=>{const m=await getManifest();if(!Object.hasOwn(m.files,file)||file.includes('..')||file.startsWith('/'))throw new Error('Unknown dataset asset');return verified(new URL(file,base()),m.files[file]);})().catch(e=>{assets.delete(file);throw e;}));return assets.get(file)!;
}
export async function readStaticRoute(path:string){const m=await getManifest(),file=m.routes[path];if(!file)throw new Error('No reviewed dataset for this route');return clone(await asset(file));}
export async function loadEngineData():Promise<EngineData>{const [anchors,policies,metadata]=await Promise.all(['anchors.json','policies.json','metadata.json'].map(asset));return {anchors,policies,metadata};}
