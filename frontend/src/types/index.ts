export type Category = string;

export interface Article {
    id: string;
    title: string;
    slug: string;
    excerpt: string | null;
    content: string | null;
    author: string | null;
    publishDate: string;
    coverImageUrl: string | null;
    category: Category;
    url: string;
}

export interface NewsData {
    articles: Article[];
}
