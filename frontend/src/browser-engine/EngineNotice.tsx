import {browserEnabled} from './mode';
import './EngineNotice.css';
export function EngineNotice(){return browserEnabled()?<nav aria-label="Portfolio home" className="engine-header"><a href="/" className="engine-home" aria-label="K. Chaturvedi home">K<span>. </span>Chaturvedi</a></nav>:null;}
