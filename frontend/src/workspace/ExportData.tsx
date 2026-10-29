import {useEffect,useState} from 'react';
export function ExportData({value,name='calculation'}:{value:unknown;name?:string}){
 const [download,setDownload]=useState<{value:unknown;href:string}|null>(null);
 useEffect(()=>{
  const href=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+'\n'],{type:'application/json'}));
  setDownload({value,href});return ()=>URL.revokeObjectURL(href);
 },[value]);
 const href=download&&download.value===value?download.href:undefined;
 return <a className="p-text-button ir-download" href={href} aria-disabled={!href||undefined} download={name.replace(/[^a-z0-9-]/gi,'-')+'.json'}>Download calculation data</a>;
}
