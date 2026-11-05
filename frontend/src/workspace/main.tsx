import React from 'react';
import {createRoot} from 'react-dom/client';
import {Workspace} from './Workspace';
import '../prototype/prototype.css';
import './workspace.css';
import {EngineNotice} from '../browser-engine/EngineNotice';
createRoot(document.getElementById('root')!).render(<React.StrictMode><EngineNotice/><Workspace/></React.StrictMode>);
