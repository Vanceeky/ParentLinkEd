
/*
var staticCacheName = 'djangopwa-v1';
 
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(staticCacheName).then(function(cache) {
      return cache.addAll([
        '',
      ]);
    })
  );
});
 
self.addEventListener('fetch', function(event) {
  var requestUrl = new URL(event.request.url);
    if (requestUrl.origin === location.origin) {
      if ((requestUrl.pathname === '/')) {
        event.respondWith(caches.match(''));
        return;
      }
    }
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
});

*/

// service-worker.js

const CACHE_NAME = 'my-cache-v1';
const OFFLINE_URL = '/offline.html';

// Install event to cache the offline page and any required assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll([
                OFFLINE_URL,
                // Pre-cache any other assets or pages you want
                '/static/assets/img/la_salette_logo.png', // example asset
            ]);
        })
    );
});

// Fetch event to cache and serve pages
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).then(response => {
            // Check if the response is valid
            if (!response || response.status !== 200 || response.type !== 'basic') {
                return response; // Return if not a valid response
            }

            // Clone the response to cache it
            const responseToCache = response.clone();

            caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, responseToCache); // Cache the page
            });

            return response; // Return the original response
        }).catch(() => {
            // If the fetch fails, serve the offline page
            return caches.match(event.request).then(response => {
                return response || caches.match(OFFLINE_URL); // Serve offline page if no match
            });
        })
    );
});

// Activate event to manage old caches
self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
