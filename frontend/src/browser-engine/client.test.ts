import {vi,it,expect,beforeEach,afterEach} from 'vitest';
import {browserResponse} from './client';
vi.mock('./data',()=>({loadEngineData:vi.fn(async()=>({anchors:{},policies:{},metadata:{}})),readStaticRoute:vi.fn(async()=>({entries:[]}))}));
class FakeWorker {
 static instances:FakeWorker[]=[];onmessage:((event:any)=>void)|null=null;onerror:(()=>void)|null=null;onmessageerror:(()=>void)|null=null;
 terminated=false;message:any;constructor(){FakeWorker.instances.push(this);}postMessage(value:any){this.message=value;}terminate(){this.terminated=true;}
}
beforeEach(()=>{FakeWorker.instances=[];vi.stubGlobal('Worker',FakeWorker);});
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
it('loads static GET data without starting a worker or financial HTTP request',async()=>{const r=await browserResponse('/api/v1/catalog',undefined);expect(await r.json()).toEqual({entries:[]});expect(FakeWorker.instances).toHaveLength(0);});
it('returns a worker result and terminates its execution',async()=>{const pending=browserResponse('/api/v1/cases/run',{case_name:'test'});await Promise.resolve();const w=FakeWorker.instances[0];expect(w.message.path).toBe('/api/v1/cases/run');w.onmessage!({data:{ok:true,result:{enterprise_value:'123'}}});expect(await (await pending).json()).toEqual({enterprise_value:'123'});expect(w.terminated).toBe(true);});
it('preserves structured validation errors',async()=>{const pending=browserResponse('/api/v1/cases/run',{});await Promise.resolve();const w=FakeWorker.instances[0];w.onmessage!({data:{ok:false,error:{code:'invalid_case',message:'Review inputs',details:['wacc: invalid']}}});const r=await pending;expect(r.status).toBe(422);expect((await r.json()).error.details).toEqual(['wacc: invalid']);expect(w.terminated).toBe(true);});
it('actually terminates an aborted worker and never starts a replacement API call',async()=>{const controller=new AbortController(),pending=browserResponse('/api/v1/cases/run',{},controller.signal);await Promise.resolve();const rejected=expect(pending).rejects.toHaveProperty('code','request_cancelled');controller.abort();await rejected;expect(FakeWorker.instances[0].terminated).toBe(true);expect(FakeWorker.instances).toHaveLength(1);});
it('terminates execution at the wall-clock deadline',async()=>{vi.useFakeTimers();const pending=browserResponse('/api/v1/cases/run',{});await Promise.resolve();const rejected=expect(pending).rejects.toHaveProperty('code','deadline_exceeded');await vi.advanceTimersByTimeAsync(35001);await rejected;expect(FakeWorker.instances[0].terminated).toBe(true);});
it('does not start an already-cancelled request',async()=>{const c=new AbortController();c.abort();await expect(browserResponse('/api/v1/cases/run',{},c.signal)).rejects.toHaveProperty('code','request_cancelled');expect(FakeWorker.instances).toHaveLength(0);});
