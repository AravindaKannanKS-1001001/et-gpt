# Separate Earth Tekniks website preview

This folder is a static mirror of public pages and assets reachable from https://etplautomation.com/. It contains no chatbot application code. Original website HTML, CSS, logos and images provide the presentation; internal links point to local copies. `mirror-manifest.json` records the captured files and any unavailable resources.

The WooCommerce `products/` shop mirror was removed (it was ~2.5 GB and is not needed for the chat preview); its nav items were stripped from the remaining pages, so no page links to it. `mirror-manifest.json` lists only the files still present.

The website injects only the existing chatbot loader script through `site/preview.js`. The default chatbot origin is `http://localhost:3100`, with widget ID 1 (the demo widget `pnpm db:seed` creates on a fresh chatbot database). The chat runs in its own iframe and backend, with its own configuration and database.

## Run locally

```sh
node server.mjs
```

Open http://localhost:3150. Set `CHAT_ORIGIN`, `WIDGET_ID`, `PORT`, or `HOST` as environment variables to change the preview configuration, e.g. `CHAT_ORIGIN=http://localhost:3100 WIDGET_ID=1 node server.mjs`. `CHAT_ORIGIN` is loaded by the visitor's browser, so it must be an address the browser can reach (never a Docker service name). The server refuses to start with an invalid value. Start the separate chatbot application on its configured origin as well.

This is a local preview of public content, not a recreation of the WordPress backend. Contact/order submissions are disabled. External videos remain external. Resources unavailable on the source site are listed in the manifest; they are not invented. Live etplautomation.com is unchanged.

## Docker

```sh
docker build -t etpl-website-preview .
docker run --rm -p 3150:8080 -e CHAT_ORIGIN=http://localhost:3100 -e WIDGET_ID=1 etpl-website-preview
```

The image contains the trimmed mirror (~30 MB after the `products/` removal). Run the chatbot separately (see `chatbot/DOCKER.md`); the preview needs only its public origin. The local preview can run without Docker.
