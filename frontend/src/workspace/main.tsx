import React from 'react';
import {createRoot} from 'react-dom/client';
import {PlatformApp} from './PlatformApp';
import '../prototype/prototype.css';
import './workspace.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><PlatformApp/></React.StrictMode>);
