// Neutral service worker — no caching, just unregisters itself
// We'll add proper caching back later

self.addEventListener('install', event => {
    console.log('[Service Worker] Neutral version installed');
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('[Service Worker] Neutral version activated — cleaning up caches');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    console.log('[Service Worker] Deleting cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
        }).then(() => self.registration.unregister())
          .then(() => self.clients.matchAll())
          .then(clients => {
              clients.forEach(client => {
                  if (client.navigate) client.navigate(client.url);
              });
          })
    );
});