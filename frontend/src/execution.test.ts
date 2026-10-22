import {it,expect,vi} from 'vitest';
import {ExecutionGate} from './execution';

it('shares one synchronous gate across EV/equity, never queues, and releases on success',async()=>{
 const gate=new ExecutionGate(),first=gate.start('ev')!;
 expect(gate.start('equity')).toBeNull();expect(gate.start('ev')).toBeNull();
 expect(await first.wait(Promise.resolve('complete'))).toBe('complete');first.finish();
 const second=gate.start('equity')!;expect(gate.start('ev')).toBeNull();second.finish();expect(gate.snapshot()).toBeNull();
});
it('cancellation discards abort-ignoring transports and old cleanup cannot release a successor',async()=>{
 const gate=new ExecutionGate(),old=gate.start('equity')!;
 let resolve!:(v:string)=>void;
 const pending=old.wait(new Promise<string>(r=>{resolve=r;}));
 const rejected=expect(pending).rejects.toMatchObject({code:'request_cancelled'});
 gate.cancel('ev');expect(gate.snapshot()).toBe('equity');gate.cancel();await rejected;
 const next=gate.start('ev')!;resolve('obsolete');old.finish();expect(gate.snapshot()).toBe('ev');next.finish();
});
it('releases a stalled calculation at the client deadline, even if transport ignores abort',async()=>{
 vi.useFakeTimers();try{
  const gate=new ExecutionGate(),lease=gate.start('ev')!;
  const rejected=expect(lease.wait(new Promise(()=>{}))).rejects.toMatchObject({code:'service_unavailable'});
  await vi.advanceTimersByTimeAsync(50000);await rejected;expect(gate.snapshot()).toBeNull();
  const next=gate.start('equity')!;lease.finish();expect(gate.snapshot()).toBe('equity');next.finish();
 }finally{vi.useRealTimers();}
});
it('releases after rejection when the caller finishes; subscribers observe shared ownership',async()=>{
 const gate=new ExecutionGate(),listener=vi.fn();const unsubscribe=gate.subscribe(listener);
 const lease=gate.start('equity')!;
 try{await lease.wait(Promise.reject(Error('failure')));}catch{}finally{lease.finish();}
 expect(gate.snapshot()).toBeNull();expect(listener).toHaveBeenCalledTimes(2);unsubscribe();
});
