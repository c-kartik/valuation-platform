/// <reference lib="webworker" />
import {runRequest} from './dispatch';
import {InputError} from './decimal';
const scope=self as unknown as DedicatedWorkerGlobalScope;
scope.onmessage=event=>{
 const {path,body,data}=event.data;
 try{scope.postMessage({ok:true,result:runRequest(path,body,data)});}
 catch(e){scope.postMessage({ok:false,error:e instanceof InputError?{code:e.code,message:e.message,details:e.details}:{code:'calculation_failed',message:'Calculation failed; no result returned.',details:[]}});}
};
