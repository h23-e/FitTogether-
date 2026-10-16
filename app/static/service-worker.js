// =================================================================
// FitTogether — Service Worker
// Handles caching for offline support and faster loading
// =================================================================

const CACHE_NAME = 'fittogether-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '<https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css>',
    '<https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js>',
    '<https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js>'
];

// Install — cache static assets
self.addEventListener('install', event => {
    console.log('[Service Worker] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('[Service Worker] Caching app shell');
            return cache.addAll(urlsToCache).catch(err => {
                console.warn('[Service Worker] Some assets failed to cache:', err);
            });
        }).then(() => self.skipWaiting())
    );
});

// Activate — clean up old caches
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Removing old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch — serve from cache, fall back to network
self.addEventListener('fetch', event => {
    // Skip non-GET requests and non-http(s) schemes
    if (event.request.method !== 'GET') return;
    if (!event.request.url.startsWith('http')) return;

    event.respondWith(
        caches.match(event.request).then(response => {
            // Return cached version if available
            if (response) return response;

            // Otherwise fetch from network
            return fetch(event.request).then(networkResponse => {
                // Don't cache non-successful or non-basic responses
                if (!networkResponse || networkResponse.status !== 200) {
                    return networkResponse;
                }

                // Cache successful responses for static files
                const url = event.request.url;
                if (url.includes('/static/') ||
                    url.includes('bootstrap') ||
                    url.includes('chart.js')) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }

                return networkResponse;
            }).catch(() => {
                // Network failed — if it's a page request, show cached home
                if (event.request.mode === 'navigate') {
                    return caches.match('/');
                }
            });
        })
    );
});