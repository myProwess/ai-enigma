import { getFeaturedArticle, getRecentArticles } from "@/lib/data";
import { ArticleCard } from "@/components/shared/ArticleCard";

export default async function Home() {
  const featuredArticle = await getFeaturedArticle();
  const recentArticles = featuredArticle
    ? await getRecentArticles(featuredArticle.id)
    : await getRecentArticles();

  return (
    <div className="w-full">
      {/* Hero Section */}
      {featuredArticle && (
        <section className="container mx-auto max-w-7xl px-4 md:px-8 py-8 md:py-12">
          <ArticleCard article={featuredArticle} featured />
        </section>
      )}

      {/* Recent News Grid */}
      <section className="container mx-auto max-w-7xl px-4 md:px-8 py-8 md:py-16">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold tracking-tight font-heading">Latest Stories</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {recentArticles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>

        {recentArticles.length === 0 && !featuredArticle && (
          <div className="text-center py-20 text-muted-foreground border rounded-xl bg-card/50">
            No articles found. Please ensure backend/data/news_data.json exists.
          </div>
        )}
      </section>
    </div>
  );
}
