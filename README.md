# AI Enigma 🗞️🤖

AI Enigma is a production-ready, full-stack news aggregation platform designed for high accessibility and premium visual aesthetics. It features a robust Python Flask backend that harvests headlines from the NewsAPI and stores them in a structured local data warehouse, paired with a cutting-edge Next.js frontend that delivers a lightning-fast, glassmorphic reading experience in both dark and light modes.

**[Live Demo 🚀](https://myprowess.github.io/ai-newsapi-repo/)**

---

## 🏗️ Architecture Overview

The project is architected with a clean separation of concerns, ensuring scalability and maintainability.

### **The Backend (Python/Flask)**
- **API Integration:** Connects to [NewsAPI](https://newsapi.org/) using a Singleton client pattern for efficient resource management.
- **Data Persistence:** Implements a service layer that transforms raw API responses into a refined JSON schema (`news_data.json`).
- **Rate Limiting & Safety:** Features an in-memory sliding window for rate limiting and atomic file writes to prevent data corruption.
- **Technologies:** Flask, requests, python-dotenv, Type Hinting (PEP 484).

### **The Frontend (Next.js/React)**
- **Framework:** Next.js 15 (App Router) with React 19 for optimal performance and SEO.
- **Styling:** A design system built on **Tailwind CSS** and **shadcn/ui**, featuring custom "glassmorphic" components and smooth transitions.
- **Typography:** Uses `@tailwindcss/typography` (prose) for a book-like reading experience on article pages.
- **Theming:** Full dark/light mode support via `next-themes` with persistent user preferences.
- **Technologies:** TypeScript (Strict Mode), Lucide React, date-fns.

---

## 🖼️ Visuals

> [!TIP]
> **Check out the `walkthrough.md` in the artifacts for a full visual guide!**

### **Main Dashboard**
![Homepage Hero & Grid](https://raw.githubusercontent.com/myProwess/ai-newsapi-repo/main/docs/homepage_screenshot.png)
*A high-impact Hero section for featured news followed by an elegant grid of recent stories.*

### **Article Reading View**
![Article Detail](https://raw.githubusercontent.com/myProwess/ai-newsapi-repo/main/docs/article_screenshot.png)
*Focused typography and clean layouts optimized for long-form reading.*

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.9+
- Node.js 18+ (npm or pnpm)
- A [NewsAPI.org](https://newsapi.org/) API Key

### **1. Backend Configuration**
```bash
cd backend
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your NEWS_API_KEY
```

### **2. Frontend Configuration**
```bash
cd frontend
# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at `http://localhost:3000`.

---

## 🛠️ Usage Examples

### **Harvesting Latest News**
The backend automatically scrapes data when endpoints are hit or via scheduled tasks:
```python
# From backend/services/news_service.py
news_service = NewsService()
news_service.fetch_and_store_top_headlines(category="technology")
```

### **Accessing the News Schema**
Articles follow a strict TypeScript interface for deterministic frontend rendering:
```typescript
interface Article {
  id: string;
  title: string;
  slug: string;
  category: "Technology" | "Business" | "Sports" | "Politics";
  content: string;
  publishDate: string;
}
```

---

## 📂 Directory Structure

```text
AI Enigma/
├── backend/                # Flask Service
│   ├── data/               # Persistent JSON storage
│   ├── routes/             # API Endpoints
│   ├── services/           # Business Logic (NewsAPI Client)
│   ├── utils/              # Loggers & Error Handlers
│   └── app.py              # Application Entry Point
├── frontend/               # Next.js Application
│   ├── src/
│   │   ├── app/            # App Router (Pages & Layouts)
│   │   ├── components/     # UI Components (shadcn/shared)
│   │   ├── lib/            # Data fetching & Utilities
│   │   └── types/          # Strict Type Definitions
│   └── public/             # Static Assets
└── .gitignore              # Unified ignore rules
```

---

## 🤝 Contribution & License

### **Contributing**
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

### **License**
Distributed under the **MIT License**. See `LICENSE` for more information.

---
*Built with ❤️ for the future of news aggregation.*
