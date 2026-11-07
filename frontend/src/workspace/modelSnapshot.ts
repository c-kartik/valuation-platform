import type {Draft,Entry} from '../model';
import type {EquityDraft} from '../equity';
import type {Session} from './useWorkspace';

export type PendingEditor={kind:'model';draft:Draft;touched:string[];resets:string[];replacementInputs:Record<string,string|undefined>}|{kind:'bridge';draft:EquityDraft};
export type AnalystSnapshot={form:Record<string,string>;status:'current'|'stale'|'not_calculated'|'calculating';result:unknown;resultForm:Record<string,string>|null;profile?:unknown};
export type ModelSnapshot={
 schema_version:'valuation-workbook-state-v1';exported_at:string;ticker:string;company_name:string;
 selected_company:string;selected_scenario:string;session:Session;entry:Entry|null;
 analyst:Record<string,AnalystSnapshot>;pending_editor:PendingEditor|null;
};
export type SnapshotSource=Omit<ModelSnapshot,'schema_version'|'exported_at'|'pending_editor'>&{pending_editor?:PendingEditor|null};
/** Freeze at click time, before loading the Excel writer or awaiting anything. */
export function captureModelSnapshot(source:SnapshotSource,now=new Date()):ModelSnapshot{
 return structuredClone({...source,schema_version:'valuation-workbook-state-v1' as const,exported_at:now.toISOString(),pending_editor:source.pending_editor??null});
}
export function modelFilename(snapshot:ModelSnapshot){
 const safe=(s:string)=>s.replace(/[^a-z0-9_-]/gi,'-').slice(0,70)||'model';
 return `${safe(snapshot.ticker)}-${safe(snapshot.selected_scenario)}-assumptions-${snapshot.exported_at.replace(/[:.]/g,'-')}.xlsx`;
}
