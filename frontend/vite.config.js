import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Frontend talks to the FastAPI backend via the /api prefix.
// In Replit's dev preview the same proxy serves both at the same origin,
// so a relative URL works automatically.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: true,
    proxy: {
      "/api": "http://localhost:8080",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
