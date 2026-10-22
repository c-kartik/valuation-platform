import {type Case,type Inputs,type Bridge,type ReverseRecord,type Variant,newCase,variantFor,signature,emptyBridge,grids,fresh} from './model';

export type Comparison={price:string;date:string};
export type ReverseForm={metric:'price'|'ev';target:string;date:string;lower:string;upper:string;mode?:'comparison'|'override'};
export type ReverseOutput={key:string;record:ReverseRecord};
export type Cell={w:string;g:string;variant?:Variant};
export type Analysis={reverse:ReverseForm;output:ReverseOutput|null;reverseAttempted:boolean;grid:string[];gridShown:string|null;cell:Cell|null};
export type Workspace={cases:Record<string,Case>;selected:string;bridge:Bridge;comparison:Comparison;analyses:Record<string,Analysis>;nextId:number};
export const newAnalysis=():Analysis=>({reverse:{metric:'price',target:'',date:'2025-12-31',lower:'-10',upper:'30',mode:'comparison'},output:null,reverseAttempted:false,grid:[...grids.standard.settings],gridShown:null,cell:null});
export function initialWorkspace():Workspace{
 const c=newCase();c.revision=1;c.shown={signature:signature(c.inputs),variant:variantFor(c.inputs)!,bridgeSignature:signature(emptyBridge())};
 return {cases:{Base:c},selected:'Base',bridge:emptyBridge(),comparison:{price:'',date:''},analyses:{Base:newAnalysis()},nextId:1};
}
export const effectiveReverse=(a:Analysis,p:Comparison):ReverseForm=>a.reverse.mode==='comparison'?{...a.reverse,metric:'price',target:p.price,date:p.date}:a.reverse;
// Only declared dependencies. EV analyses do not depend on the equity bridge.
export const reverseKey=(id:string,c:Case,f:ReverseForm,b:Bridge)=>signature([id,c.revision,c.inputs,f,f.metric==='price'?b:null]);
export const gridKey=(id:string,c:Case,settings:string[])=>signature([id,c.revision,c.inputs,settings]);
export const reverseCurrent=(s:Workspace,id:string)=>{const a=s.analyses[id];return Boolean(a?.output&&fresh(s.cases[id])&&a.output.key===reverseKey(id,s.cases[id],effectiveReverse(a,s.comparison),s.bridge));};
export const gridCurrent=(s:Workspace,id:string)=>{const a=s.analyses[id];return Boolean(a?.gridShown&&fresh(s.cases[id])&&a.gridShown===gridKey(id,s.cases[id],a.grid));};
export function editInputs(s:Workspace,id:string,inputs:Inputs):Workspace{
 if(signature(inputs)===signature(s.cases[id].inputs))return s;
 return {...s,cases:{...s.cases,[id]:{...s.cases[id],inputs,revision:(s.cases[id].revision??1)+1}}};
}
export function forkCase(s:Workspace,source:string,inputs:Inputs,description:string):Workspace{
 const id=`Exploratory ${s.nextId}`;
 return {...s,nextId:s.nextId+1,selected:id,cases:{...s.cases,[id]:{inputs:structuredClone(inputs),notes:'',revision:1,relation:{source,revision:s.cases[source].revision??1,description}}},analyses:{...s.analyses,[id]:newAnalysis()}};
}
export const impliedInputs=(c:Case,growth:string):Inputs=>({...structuredClone(c.inputs),annual:c.inputs.annual.map(y=>({...y,growth}))});
export const rateInputs=(c:Case,wacc:string,g:string):Inputs=>({...structuredClone(c.inputs),wacc,g});
