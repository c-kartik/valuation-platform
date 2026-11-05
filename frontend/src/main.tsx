import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import './style.css';
import {EngineNotice} from './browser-engine/EngineNotice';

createRoot(document.getElementById('root')!).render(<React.StrictMode><EngineNotice/><App /></React.StrictMode>);
