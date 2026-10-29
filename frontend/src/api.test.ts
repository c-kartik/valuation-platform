import {it,expect,vi,afterEach} from 'vitest';
import {request,failureMessage,unavailableMessage,timeoutMessage,ApiError} from './api';
afterEach(()=>vi.unstubAllGlobals());
it.each([500,502,503])('handles non-JSON gateway %s without exposing HTML',async(status)=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response('<html>private traceback</html>',{status})));
 await expect(request('/api/v1/cases/run',{})).rejects.toMatchObject({code:'service_unavailable',message:unavailableMessage});
});
it.each(['null','[]','{}','not JSON','{"stage_b":{"years":[],"stage_a":{}}}'])('rejects malformed successful calculation response %s',async(body)=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(body,{status:200})));
 await expect(request('/api/v1/cases/run',{})).rejects.toMatchObject({code:'service_unavailable'});
});
it('keeps validation errors bounded and field-specific; hides server exception text',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({error:{code:'invalid_case',message:'secret traceback',details:['wacc: correct this',{},...Array(25).fill('x'.repeat(300))]}}),{status:422})));
 await expect(request('/api/v1/cases/run',{})).rejects.toMatchObject({code:'invalid_case',message:'Review the indicated inputs.',details:expect.arrayContaining(['wacc: correct this'])});
 try{await request('/api/v1/cases/run',{});}catch(e){expect((e as ApiError).details).toHaveLength(20);expect((e as ApiError).details[1]).toHaveLength(200);}
});
it('distinguishes busy from unavailable and does not diagnose a budget cap',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response('gateway',{status:429})));
 try{await request('/api/v1/cases/run',{});}catch(e){expect(failureMessage(e)).toMatch(/in progress/);}
 expect(failureMessage(new ApiError('internal_error','private traceback'))).toBe(unavailableMessage);
 expect(unavailableMessage).not.toMatch(/budget|cap/i);
});
it('network failure preserves submitted data and never retries automatically',async()=>{
 const body={notes:'keep',bridge:{assets:'12'}},before=JSON.stringify(body),fetch=vi.fn(async()=>{throw Error('offline');});vi.stubGlobal('fetch',fetch);
 await expect(request('/api/v1/cases/run',body)).rejects.toMatchObject({message:unavailableMessage});
 expect(JSON.stringify(body)).toBe(before);expect(fetch).toHaveBeenCalledTimes(1);
});

it.each([{}, {scenarios:[]}, {scenarios:[{label:'Bear',result:{}}]}])('rejects malformed scenario success without rendering a partial set',async(body)=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify(body),{status:200})));
 await expect(request('/api/v1/scenarios/run',{scenarios:[]})).rejects.toMatchObject({code:'service_unavailable'});
});

it.each(['/api/v1/sensitivity/run','/api/v1/reverse/run'])('rejects malformed analysis results on %s',async path=>{
 for(const body of [{},{schema_version:'investor-reverse-dcf-results-v1',status:'SUCCESS',solution:null},{schema_version:'investor-sensitivity-results-v1',cells:[]}]){vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify(body),{status:200})));await expect(request(path,{})).rejects.toMatchObject({code:'service_unavailable'});}
});

it('distinguishes deadline from busy and unavailable without promising worker cancellation',()=>{
 expect(failureMessage(new ApiError('deadline_exceeded','untrusted server text'))).toBe(timeoutMessage);
 expect(timeoutMessage).toMatch(/inputs are still here/);expect(timeoutMessage).toMatch(/server work may continue/);
 expect(timeoutMessage).not.toBe(unavailableMessage);
});
it('classifies the transport waiting deadline separately and retains the submitted body',async()=>{
 vi.useFakeTimers();try{
  const body={untouched:'test'};
  vi.stubGlobal('fetch',vi.fn((_url,options)=>new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(Error('aborted'))))));
  const pending=expect(request('/api/v1/cases/run',body)).rejects.toMatchObject({code:'deadline_exceeded'});
  await vi.advanceTimersByTimeAsync(50000);await pending;expect(body).toEqual({untouched:'test'});
 }finally{vi.useRealTimers();}
});

it('handles an HTTP 504 timeout without rendering gateway HTML',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>new Response('<html>private traceback</html>',{status:504})));
 await expect(request('/api/v1/reverse/run',{})).rejects.toMatchObject({code:'deadline_exceeded',message:timeoutMessage});
});
