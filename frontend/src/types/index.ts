export type Category = "Technology" | "Business" | "Sports" | "Politics";

export interface Article {
    id: string;
    title: string;
    slug: string;
    excerpt: string;
    content: string;
    author: string;
    publishDate: string;
    coverImageUrl: string;
    category: Category;
}

export interface NewsData {
    articles: Article[];
}
