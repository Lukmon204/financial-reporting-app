const CACHE_NAME = 'financial-reporting-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/manifest.json'
];

// Установка кэша
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Обработка запросов
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Возвращаем кэшированный ответ, если он есть
                if (response) {
                    return response;
                }

                // Клонируем запрос для сетевого запроса
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest).then(
                    response => {
                        // Проверяем валидность ответа
                        if(!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Кэшируем ответ
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    }
                );
            })
    );
});

// Активация нового SW
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