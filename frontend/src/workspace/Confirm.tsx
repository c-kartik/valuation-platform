import {useEffect,useRef} from 'react';
export type Confirmation={title:string;body:string;accept:string;action:()=>void};
export function Confirm({value,close}:{value:Confirmation;close:()=>void}){
 const ref=useRef<HTMLDialogElement>(null),opener=useRef(document.activeElement as HTMLElement|null);
 useEffect(()=>{const dialog=ref.current!;dialog.showModal();dialog.querySelector<HTMLButtonElement>('[data-keep]')?.focus();return()=>{dialog.close();const restore=()=>{if(opener.current?.isConnected)opener.current.focus();};restore();requestAnimationFrame(()=>{if(document.activeElement===document.body)restore();});};},[]);
 return <dialog ref={ref} className="p-dialog" aria-label={value.title} onCancel={e=>{e.preventDefault();close();}}><h2>{value.title}</h2><p>{value.body}</p><div className="p-actions"><button data-keep onClick={close}>Keep current inputs</button><button className="p-primary" onClick={()=>{value.action();close();}}>{value.accept}</button></div></dialog>;
}
