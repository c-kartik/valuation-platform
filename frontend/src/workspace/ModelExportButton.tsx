import {useRef,useState} from 'react';
import type {ModelSnapshot} from './modelSnapshot';
import {modelFilename} from './modelSnapshot';
import './ModelExport.css';

export function ModelExportButton({snapshot}:{snapshot:()=>ModelSnapshot}){
 const [busy,setBusy]=useState(false),[failure,setFailure]=useState('');
 const running=useRef(false);
 async function download(){
  if(running.current)return;
  running.current=true;setBusy(true);setFailure('');
  try{
   const captured=snapshot();
   const {writeModelWorkbook}=await import('./modelWorkbook');
   const bytes=await writeModelWorkbook(captured);
   const href=URL.createObjectURL(new Blob([bytes],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));
   const link=document.createElement('a');link.href=href;link.download=modelFilename(captured);document.body.append(link);link.click();link.remove();
   // Keep the object URL alive long enough for Safari to start the download.
   setTimeout(()=>URL.revokeObjectURL(href),60_000);
  }catch{setFailure('Excel download did not complete. Your model is unchanged. Please try again.');}
  finally{running.current=false;setBusy(false);}
 }
 return <span className="model-export"><button type="button" disabled={busy} onClick={()=>void download()}>{busy?'Preparing Excel…':'Download Excel'}</button>{failure&&<span role="alert">{failure}</span>}</span>;
}
