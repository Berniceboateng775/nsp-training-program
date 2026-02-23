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

  async getRecommendations(query, genres, mood) {
    return this.request("/recommend", {
      method: "POST",
      body: JSON.stringify({ query, genres, mood }),
    });
  }

  async getTrending() {
    return this.request("/recommend/trending");
  }

  // ─── Emotions ────────────────────────────────────────

  async analyzeEmotions(text) {
    return this.request("/emotions/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
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
