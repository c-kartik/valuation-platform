/** Shared local-case execution path for the calculator and integrated workspace. */
import {request} from './api';
import type {ExecutionGate} from './execution';
import type {InvestorDoc,InvestorEquityDoc,Result} from './model';
export async function executeCase<T>({gate,action,operation='run',build,load=request,current,check}:{
 gate:ExecutionGate;action:'ev'|'equity';operation?:'validate'|'run';
 build:()=>InvestorDoc|InvestorEquityDoc;load?:typeof request;current:()=>boolean;check?:(value:T)=>void;
}):Promise<T|undefined>{
 const lease=gate.start(action);if(!lease)return undefined;
 try{
  const body=build();
  const value=await lease.wait(load<T>(`/api/v1/cases/${operation}`,body,lease.signal));
  if(lease.signal.aborted||!current())return undefined;
  check?.(value);return value;
 }catch(error){if(!current())return undefined;throw error;}
 finally{lease.finish();}
}
export function requireMatchingEquity(value:Result,ev:Result){
 if(!value.stage_c||JSON.stringify(value.stage_b)!==JSON.stringify(ev.stage_b))throw new Error('Equity response does not match the current enterprise-value calculation.');
}
