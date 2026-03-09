/**
 * Vellichor AI — API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = "http://localhost:8000/api";

class VellichorAPI {
  constructor() {
    this.token = localStorage.getItem("vellichor_token");
  }

  // ─── Auth Headers ────────────────────────────────────

  getHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem("vellichor_token", token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem("vellichor_token");
    localStorage.removeItem("vellichor_user");
  }

  setUser(user) {
    localStorage.setItem("vellichor_user", JSON.stringify(user));
  }

  getUser() {
    const data = localStorage.getItem("vellichor_user");
    return data ? JSON.parse(data) : null;
  }

  isLoggedIn() {
    return !!this.token;
  }

  // ─── Generic Request ─────────────────────────────────

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed");
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ─── Auth ────────────────────────────────────────────

  async register(name, email, password, favoriteGenres) {
    const data = await this.request("/register", {
      method: "POST",
      body: JSON.stringify({
        name,
        email,
        password,
        favorite_genres: favoriteGenres,
      }),
    });
    this.setToken(data.access_token);
    this.setUser(data.user);
    return data;
  }

  async login(email, password) {
    const data = await this.request("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    this.setUser(data.user);
    return data;
  }

  logout() {
    this.clearToken();
    window.location.href = "index.html";
  }

  // ─── Chat ────────────────────────────────────────────

  async sendMessage(message, conversationId = null) {
    return this.request("/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  }

  async getChatHistory() {
    return this.request("/chat/history");
  }

  // ─── Recommendations ─────────────────────────────────

  async getRecommendations() {
    return this.request("/recommend", { method: "POST" });
  }

  async getTrending() {
    return this.request("/recommend/trending");
  }

  async searchBooks(query) {
    return this.request(`/recommend/search?q=${encodeURIComponent(query)}`);
  }

  async getBookDetails(workId) {
    return this.request(`/recommend/book/${workId}`);
  }

  // ─── Emotions ────────────────────────────────────────

  async analyzeEmotions(text, situation = '') {
    return this.request("/emotions/analyze", {
      method: "POST",
      body: JSON.stringify({ text, situation }),
    });
  }

  async analyzeFile(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    const url = `${API_BASE}/emotions/analyze-file`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Authorization": `Bearer ${this.token}` },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "File analysis failed");
    return data;
  }

  async uploadEmotionDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    const url = `${API_BASE}/emotions/upload`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Authorization": `Bearer ${this.token}` },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Upload failed");
    return data;
  }

  async queryAnalyze(query) {
    return this.request("/emotions/query-analyze", {
      method: "POST",
      body: JSON.stringify({ text: query }),
    });
  }

  async uploadChatDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    const url = `${API_BASE}/chat/upload`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Authorization": `Bearer ${this.token}` },
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Upload failed");
    return data;
  }

  // ─── Profile ─────────────────────────────────────────

  async getProfile() {
    return this.request("/profile");
  }

  async updateProfile(data) {
    return this.request("/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async getReadingList() {
    return this.request("/profile/reading-list");
  }

  async addToReadingList(book) {
    return this.request("/profile/reading-list", {
      method: "POST",
      body: JSON.stringify(book),
    });
  }
}

// Global API instance
const api = new VellichorAPI();
