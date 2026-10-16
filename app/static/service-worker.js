// =================================================================
// FitTogether — Service Worker
// Handles caching for offline support and faster loading
// =================================================================

const CACHE_NAME = 'fittogether-v2';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js'
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
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Skip non-http(s) schemes (chrome-extension://, etc.)
    if (!event.request.url.startsWith('http')) return;

    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            // Return cached version if available
            if (cachedResponse) {
                return cachedResponse;
            }

            // Otherwise fetch from network
            return fetch(event.request).then(networkResponse => {
                // Cache successful responses for static files
                if (networkResponse && networkResponse.status === 200) {
                    const url = event.request.url;
                    if (url.includes('/static/') ||
                        url.includes('bootstrap') ||
                        url.includes('chart.js')) {
                        const responseClone = networkResponse.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    }
                }
                return networkResponse;
            }).catch(err => {
                // Network failed — return a valid fallback Response
                console.warn('[Service Worker] Network failed for:', event.request.url);

                // For navigation requests (page loads), try cached homepage
                if (event.request.mode === 'navigate') {
                    return caches.match('/').then(cachedHome => {
                        if (cachedHome) {
                            return cachedHome;
                        }
                        // Nothing in cache either — return a valid offline Response
                        return new Response(
                            '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Offline</title>' +
                            '<style>body{font-family:Arial,sans-serif;text-align:center;padding:50px;background:#1A2D47;color:#fff;}' +
                            'h1{color:#FF5C1A;font-size:2rem;}p{color:#ccc;}</style></head>' +
                            '<body><h1>🏋️ You\'re offline</h1>' +
                            '<p>FitTogether couldn\'t load the page. Please check your internet connection and try again.</p>' +
                            '</body></html>',
                            {
                                status: 200,
                                statusText: 'OK',
                                headers: { 'Content-Type': 'text/html' }
                            }
                        );
                    });
                }

                // For other requests, return a basic error Response
                return new Response('Network error', {
                    status: 503,
                    statusText: 'Service Unavailable',
                    headers: { 'Content-Type': 'text/plain' }
                });
            });
        })
    );
});