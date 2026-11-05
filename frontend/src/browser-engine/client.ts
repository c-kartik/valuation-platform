import {loadEngineData,readStaticRoute} from './data';
import {ApiError} from '../api';
export async function browserResponse(path:string,body:unknown,signal?:AbortSignal):Promise<Response>{
 if(signal?.aborted)throw new ApiError('request_cancelled','Calculation cancelled. Your inputs are still here. Retry when ready.');
 if(body===undefined){try{return Response.json(await readStaticRoute(path));}catch{throw new ApiError('service_unavailable','Prepared company data is unavailable or failed its integrity check.');}}
 const data=await loadEngineData();if(signal?.aborted)throw new ApiError('request_cancelled','Calculation cancelled. Your inputs are still here. Retry when ready.');
 return new Promise((resolve,reject)=>{
  const worker=new Worker(new URL('./worker.ts',import.meta.url),{type:'module'});
  const finish=()=>{worker.terminate();clearTimeout(timer);signal?.removeEventListener('abort',abort);};
  const abort=()=>{finish();reject(new ApiError('request_cancelled','Calculation cancelled. Your inputs are still here. Retry when ready.'));};
  const timer=setTimeout(()=>{finish();reject(new ApiError('deadline_exceeded','Calculation stopped after exceeding the on-device time limit. Your inputs are still here.'));},35000);
  signal?.addEventListener('abort',abort,{once:true});
  worker.onmessage=event=>{finish();const reply=event.data;resolve(Response.json(reply.ok?reply.result:{error:reply.error},{status:reply.ok?200:reply.error?.code==='invalid_case'?422:500}));};
  worker.onerror=()=>{finish();reject(new ApiError('calculation_failed','The on-device calculation failed. Your inputs are still here.'));};
  worker.onmessageerror=()=>{finish();reject(new ApiError('calculation_failed','Could not read the on-device result.'));};
  worker.postMessage({path,body,data});
 });
}
