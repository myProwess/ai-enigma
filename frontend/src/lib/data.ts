import fs from "fs";
import path from "path";
import { Article, NewsData } from "@/types";

// Helper to read the JSON file directly
function getNewsData(): NewsData {
    try {
        // The path is relative to the project root (where Next.js is running)
        // frontend/ is beside backend/
        const dataPath = path.join(process.cwd(), "..", "backend", "data", "news_data.json");
        const fileContents = fs.readFileSync(dataPath, "utf8");
        return JSON.parse(fileContents) as NewsData;
    } catch (error) {
        console.error("Error reading news_data.json:", error);
        return { articles: [] };
    }
}

export async function getAllArticles(): Promise<Article[]> {
    const data = getNewsData();
    // Sort by date descending (newest first)
    return data.articles.sort(
        (a, b) => new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime()
    );
}

export async function getFeaturedArticle(): Promise<Article | null> {
    const articles = await getAllArticles();
    return articles.length > 0 ? articles[0] : null;
}

export async function getRecentArticles(excludeId?: string): Promise<Article[]> {
    const articles = await getAllArticles();
    if (excludeId) {
        return articles.filter((a) => a.id !== excludeId);
    }
    return articles;
}

export async function getArticlesByCategory(categorySlug: string): Promise<Article[]> {
    const articles = await getAllArticles();
    // Map category slugs (e.g. "technology") to actual exact categories
    const normalizedSlug = categorySlug.toLowerCase();

    return articles.filter(
        (a) => a.category.toLowerCase() === normalizedSlug
    );
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
    const articles = await getAllArticles();
    return articles.find((a) => a.slug === slug) || null;
}

export async function getUniqueCategories(): Promise<string[]> {
    const articles = await getAllArticles();
    const categorySet = new Set(articles.map((a) => a.category));
    return Array.from(categorySet).sort();
}
