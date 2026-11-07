import {browserEnabled} from './mode';
import './EngineNotice.css';
export function EngineNotice(){return browserEnabled()?<aside aria-label="Calculation mode" className="engine-header"><a href="/" className="engine-home" aria-label="K. Chaturvedi home">K<span>. </span>Chaturvedi</a><span className="engine-notice">Browser preview · Calculations run on your device · Company data is a prepared snapshot</span></aside>:null;}
