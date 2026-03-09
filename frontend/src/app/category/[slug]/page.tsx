import { notFound } from "next/navigation";
import { getArticlesByCategory, getUniqueCategories } from "@/lib/data";
import { ArticleCard } from "@/components/shared/ArticleCard";

interface CategoryPageProps {
    params: Promise<{
        slug: string;
    }>;
}

export async function generateStaticParams() {
    const categories = await getUniqueCategories();
    return categories.map((cat) => ({
        slug: cat.toLowerCase(),
    }));
}

export default async function CategoryPage({ params }: CategoryPageProps) {
    const { slug } = await params;

    const articles = await getArticlesByCategory(slug);

    if (articles.length === 0) {
        notFound();
    }

    // Format slug to title case (e.g., "technology" -> "Technology")
    const categoryTitle = slug.charAt(0).toUpperCase() + slug.slice(1);

    return (
        <div className="container mx-auto max-w-7xl px-4 md:px-8 py-12 md:py-16">
            <div className="mb-10 animate-in slide-in-from-bottom-4 duration-500">
                <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 font-heading">
                    {categoryTitle} News
                </h1>
                <p className="text-lg text-muted-foreground font-body">
                    The latest stories and headlines from the world of {categoryTitle.toLowerCase()}.
                </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
                {articles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                ))}
            </div>
        </div>
    );
}
