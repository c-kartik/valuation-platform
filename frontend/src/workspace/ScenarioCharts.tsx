import type {Entry,Result} from '../model';
import {OperatingCharts} from './OperatingCharts';
export function ScenarioCharts({cases,stale=false,entry}:{cases:{label:string;result:Result}[];stale?:boolean;entry?:Entry}){
 return <OperatingCharts cases={cases} scenario stale={stale} entry={entry}/>;
}
