import {browserEnabled} from './mode';
import type {ReactNode} from 'react';
import './EngineNotice.css';
export function EngineNotice({children}:{children?:ReactNode}){return browserEnabled()||children?<nav aria-label="Portfolio home" className="engine-header"><a href="/" className="engine-home" aria-label="K. Chaturvedi home">K<span>. </span>Chaturvedi</a>{children}</nav>:null;}
