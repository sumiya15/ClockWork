import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './app/App.jsx';
import DemoApp from './demo/DemoApp.jsx';
import './demo/demo.css';
import './styles/index.css';

const Root = import.meta.env.VITE_APP_MODE === 'api' ? App : DemoApp;
createRoot(document.getElementById('root')).render(<React.StrictMode><Root /></React.StrictMode>);
