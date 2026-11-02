import type {Entry,Result} from '../model';
import type {ChartInspection} from './chartInspection';
import {OperatingCharts} from './OperatingCharts';
export function ForecastChart({cases,comparison=false,entry,inspection=null,stale=false}:{cases:{label:string;result:Result}[];comparison?:boolean;entry?:Entry;inspection?:ChartInspection|null;stale?:boolean}){
 return <OperatingCharts cases={cases} scenario={comparison} entry={entry} inspection={inspection} stale={stale}/>;
}
