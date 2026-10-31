import type {Entry,Result} from '../model';
import {OperatingCharts} from './OperatingCharts';
export function ForecastChart({cases,comparison=false,entry}:{cases:{label:string;result:Result}[];comparison?:boolean;entry?:Entry}){
 return <OperatingCharts cases={cases} scenario={comparison} entry={entry}/>;
}
