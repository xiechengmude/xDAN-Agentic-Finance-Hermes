import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/",
  resolve: {
    alias: {
      "@": path.resolve(new URL(".", import.meta.url).pathname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      // Proxy API requests to the backend server
      "/assistants": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        ws: true,
      },
      // Transform standalone /threads calls to use the assistant-based endpoints
      "/threads": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        ws: true,
        rewrite: (path) => {
          // Extract assistant ID from common usage patterns
          const assistantId = "xdan-agent"; // Default assistant ID used in App.tsx
          
          // Handle different thread endpoint patterns
          if (path === "/threads") {
            // POST /threads -> POST /assistants/{assistant_id}/threads
            return `/assistants/${assistantId}/threads`;
          } else if (path.match(/^\/threads\/([^\/]+)$/)) {
            // GET /threads/{threadId} -> GET /assistants/{assistant_id}/threads/{threadId}
            const threadId = path.split("/")[2];
            return `/assistants/${assistantId}/threads/${threadId}`;
          } else if (path.match(/^\/threads\/([^\/]+)\/runs\/stream$/)) {
            // POST /threads/{threadId}/runs/stream -> POST /assistants/{assistant_id}/threads/{threadId}/runs/stream
            const threadId = path.split("/")[2];
            return `/assistants/${assistantId}/threads/${threadId}/runs/stream`;
          } else if (path.match(/^\/threads\/([^\/]+)\/history$/)) {
            // POST /threads/{threadId}/history -> POST /assistants/{assistant_id}/threads/{threadId}/history
            const threadId = path.split("/")[2];
            return `/assistants/${assistantId}/threads/${threadId}/history`;
          } else if (path.match(/^\/threads\/([^\/]+)\/state/)) {
            // GET /threads/{threadId}/state -> GET /assistants/{assistant_id}/threads/{threadId}/state
            const threadId = path.split("/")[2];
            const remaining = path.substring(`/threads/${threadId}`.length);
            return `/assistants/${assistantId}/threads/${threadId}${remaining}`;
          } else if (path.match(/^\/threads\/([^\/]+)\//)) {
            // Handle any other thread-specific endpoints
            const threadId = path.split("/")[2];
            const remaining = path.substring(`/threads/${threadId}`.length);
            return `/assistants/${assistantId}/threads/${threadId}${remaining}`;
          }
          
          // Default fallback - should not happen
          return path;
        }
      },
      "/health": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/tools": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://127.0.0.1:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
