import {useRef, useSyncExternalStore} from 'react';
import {ApiError, unavailableMessage} from './api';

type Action = 'ev' | 'equity';
// One synchronous gate per mounted client, shared by both calculation actions.
// Identity-checked release prevents a cancelled request's finally from releasing its successor.
export class ExecutionGate {
  private active: {action: Action; controller: AbortController} | null = null;
  private listeners = new Set<() => void>();
  subscribe = (listener: () => void) => {this.listeners.add(listener); return () => {this.listeners.delete(listener);};};
  snapshot = () => this.active?.action ?? null;
  private notify() {this.listeners.forEach(listener => listener());}
  cancel(action?: Action) {
    if (this.active && (!action || this.active.action === action)) {
      this.active.controller.abort(new ApiError('request_cancelled', 'Calculation cancelled. Your inputs are still here. Retry when ready.'));
    }
  }
  start(action: Action) {
    if (this.active) return null; // Never queue or replace an in-flight calculation.
    const owner = {action, controller: new AbortController()};
    this.active = owner;
    const {signal} = owner.controller;
    const finish = () => {
      clearTimeout(timer);
      if (this.active === owner) {this.active = null; this.notify();}
    };
    const timer = setTimeout(() => owner.controller.abort(new ApiError('service_unavailable', unavailableMessage)), 50000);
    signal.addEventListener('abort', finish, {once: true});
    this.notify();
    return {
      signal,
      finish: () => {signal.removeEventListener('abort', finish); finish();},
      wait: <T,>(operation: Promise<T>): Promise<T> => new Promise((resolve, reject) => {
        const abort = () => reject(signal.reason);
        operation.then(resolve, reject).finally(() => signal.removeEventListener('abort', abort));
        if (signal.aborted) reject(signal.reason);
        else signal.addEventListener('abort', abort, {once: true});
      }),
    };
  }
}
export function useExecutionGate(shared?: ExecutionGate) {
  const local = useRef<ExecutionGate | null>(null);
  if (!local.current) local.current = new ExecutionGate();
  const gate = shared ?? local.current;
  const action = useSyncExternalStore(gate.subscribe, gate.snapshot);
  return {gate, action};
}
