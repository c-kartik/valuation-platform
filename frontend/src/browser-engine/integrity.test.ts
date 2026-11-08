import {vi,it,expect,beforeEach,afterEach} from 'vitest';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {webcrypto} from 'node:crypto';
beforeEach(()=>{vi.resetModules();vi.stubGlobal('crypto',webcrypto);});
afterEach(()=>vi.unstubAllGlobals());
function transport(tamper?:string){
 const calls:string[]=[];vi.stubGlobal('fetch',vi.fn(async(url:URL)=>{const file=String(url).split('/browser-data/')[1];calls.push(file);const bytes=readFileSync(resolve('public/browser-data',file));const body=tamper===file?Buffer.concat([bytes,Buffer.from(' ')]):bytes;const response=new Response(body,{status:200});/* Preserve the Node buffer realm for WebCrypto under jsdom. */response.arrayBuffer=async()=>body.buffer.slice(body.byteOffset,body.byteOffset+body.byteLength) as ArrayBuffer;return response;}));return calls;
}
it('loads verified static data and returns a separate object per caller',async()=>{const calls=transport(),{readStaticRoute}=await import('./data');const first=await readStaticRoute('/api/v1/catalog');first.entries.length=0;const second=await readStaticRoute('/api/v1/catalog');expect(second.entries).toHaveLength(3);expect(calls).toEqual(['manifest.json','catalog.json']);});
it('rejects a modified manifest before reading a company asset',async()=>{const calls=transport('manifest.json'),{readStaticRoute}=await import('./data');await expect(readStaticRoute('/api/v1/catalog')).rejects.toThrow('integrity');expect(calls).toEqual(['manifest.json']);});
it('rejects modified data rather than using a cloud fallback',async()=>{const calls=transport('catalog.json'),{readStaticRoute}=await import('./data');await expect(readStaticRoute('/api/v1/catalog')).rejects.toThrow('integrity');expect(calls).toEqual(['manifest.json','catalog.json']);});
it('loads the complete engine context from verified files only',async()=>{const calls=transport(),{loadEngineData}=await import('./data');const d=await loadEngineData();expect(Object.keys(d.policies).sort()).toEqual(['AAPL','GOOGL','META']);expect(calls.sort()).toEqual(['anchors.json','manifest.json','metadata.json','policies.json']);});
