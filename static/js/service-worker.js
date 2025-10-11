// =====================================================
// 🏡 Service Worker - Celo Imóveis
// Suporte offline + cache inteligente + página de fallback
// =====================================================

const CACHE_NAME = "celo-imoveis-cache-v2";

// 🗂️ Lista de arquivos para cache inicial
const urlsToCache = [
  "/",
  "/offline.html",
  "/static/css/custom.css",
  "/static/img/logo.png",
  "/static/img/favicon-32x32.png",
  "/static/img/favicon-192x192.png",
  "/static/img/favicon-512x512.png",
  "/static/img/favicon.ico",
  "/static/manifest.json"
];

// 🧱 Instalação
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("🧩 Cache inicial criado!");
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

// ♻️ Ativação (remove caches antigos)
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log("🗑️ Removendo cache antigo:", name);
            return caches.delete(name);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// 🌐 Intercepta requisições (modo offline inteligente)
self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Se resposta válida, salva no cache
        if (!response || response.status !== 200 || response.type !== "basic") {
          return response;
        }
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      })
      .catch(() => {
        // 📴 Se offline, exibe a página de fallback
        return caches.match(event.request).then((cachedResponse) => {
          return cachedResponse || caches.match("/offline.html");
        });
      })
  );
});

