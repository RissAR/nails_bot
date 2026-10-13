import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './index.css';

// Client-side cache-busting and storage cleanup
(function cleanStorageAndCache() {
  try {
    const params = new URLSearchParams(window.location.search);
    const currentVersion = params.get('v') || '1.0.1';
    const storedVersion = localStorage.getItem('sense_app_version');

    if (storedVersion !== currentVersion) {
      // 1. Clear browser Cache Storage
      if ('caches' in window) {
        caches.keys().then((names) => {
          names.forEach((name) => caches.delete(name));
        }).catch(() => {});
      }

      // 2. Clear stale non-essential localStorage data
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && !key.startsWith('sense_essential_')) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach((k) => localStorage.removeItem(k));
      localStorage.setItem('sense_app_version', currentVersion);
    } else {
      // Memory overflow guard (check total storage size)
      let totalLength = 0;
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key) {
          totalLength += key.length + (localStorage.getItem(key)?.length || 0);
        }
      }
      // If exceeds ~5MB safety threshold, prune non-essential items
      if (totalLength > 5 * 1024 * 1024) {
        const keysToRemove: string[] = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && !key.startsWith('sense_essential_') && key !== 'sense_app_version') {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach((k) => localStorage.removeItem(k));
      }
    }
  } catch (err) {
    console.warn('Storage cleanup warning:', err);
  }
})();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
