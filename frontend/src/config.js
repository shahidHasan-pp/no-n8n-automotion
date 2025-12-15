// API Configuration for Network Demo
// Change this IP if your computer's network IP changes
const NETWORK_IP = "192.168.5.12";

// Automatically detect if we're on localhost or network
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

const API_BASE_URL = isLocalhost
    ? "http://localhost:8000/api/v1"  // Use localhost when accessing via localhost
    : `http://${NETWORK_IP}:8000/api/v1`;  // Use network IP when accessing via network

// Debug: Log the API URL being used
console.log("🌐 API Base URL:", API_BASE_URL);
console.log("📍 Current Host:", window.location.hostname);
console.log("🔍 Is Localhost:", isLocalhost);

export default API_BASE_URL;
