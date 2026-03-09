import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { format } from "date-fns";
import { ArrowLeft, Clock, ExternalLink } from "lucide-react";
import { getArticleBySlug, getArticlesByCategory, getAllArticles } from "@/lib/data";
import { Badge } from "@/components/ui/badge";
import { ArticleCard } from "@/components/shared/ArticleCard";

interface ArticlePageProps {
    params: Promise<{
        slug: string;
    }>;
}

export async function generateStaticParams() {
    const articles = await getAllArticles();
    return articles.map((article) => ({
        slug: article.slug,
    }));
}

export default async function ArticlePage({ params }: ArticlePageProps) {
    const { slug } = await params;
    const article = await getArticleBySlug(slug);

    if (!article) {
        notFound();
    }

    // Fetch related articles (same category, exclude current)
    const categoryArticles = await getArticlesByCategory(article.category);
    const relatedArticles = categoryArticles
        .filter((a) => a.id !== article.id)
        .slice(0, 3);

    const formattedDate = format(new Date(article.publishDate), "MMMM d, yyyy");

    const PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1600&auto=format&fit=crop";
    const authorName = article.author || "News Desk";
    const authorInitial = authorName.charAt(0);
    const contentParagraphs = article.content ? article.content.split('\n\n') : [];
    const imageUrl = article.coverImageUrl || PLACEHOLDER_IMAGE;

    return (
        <article className="min-h-screen pb-16">
            <div className="container mx-auto max-w-7xl px-4 md:px-8 py-8">
                <Link
                    href="/"
                    className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-foreground transition-colors mb-8"
                >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to home
                </Link>

                {/* Article Header */}
                <header className="max-w-4xl mx-auto text-center mb-10">
                    <Badge category={article.category} className="mb-6 px-3 py-1 text-sm shadow-sm hover:scale-105 transition-transform">
                        {article.category}
                    </Badge>
                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight mb-6 leading-tight font-heading">
                        {article.title}
                    </h1>
                    {article.excerpt && (
                        <p className="text-xl text-muted-foreground mb-8 text-balance mx-auto font-body leading-relaxed">
                            {article.excerpt}
                        </p>
                    )}
                    <div className="flex items-center justify-center space-x-6 text-sm font-medium text-muted-foreground border-y py-4">
                        <span className="flex items-center">
                            <span className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3 font-bold">
                                {authorInitial}
                            </span>
                            {authorName}
                        </span>
                        <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-2" />
                            {formattedDate}
                        </span>
                    </div>
                </header>
            </div>

            {/* Featured Image */}
            <div className="w-full max-w-6xl mx-auto px-4 md:px-8 mb-16">
                <div className="relative aspect-[21/9] overflow-hidden rounded-2xl shadow-xl">
                    <Image
                        src={imageUrl}
                        alt={article.title}
                        fill
                        className="object-cover"
                        priority
                        sizes="100vw"
                    />
                </div>
            </div>

            {/* Article Content */}
            <div className="container mx-auto px-4 md:px-8 max-w-3xl">
                <div className="prose prose-lg dark:prose-invert prose-headings:font-heading prose-headings:font-bold prose-headings:tracking-tight prose-p:font-body prose-p:leading-[1.85] prose-p:text-foreground/90 prose-a:text-primary prose-a:font-medium prose-img:rounded-xl mx-auto">
                    {contentParagraphs.length > 0 ? (
                        contentParagraphs.map((paragraph, index) => (
                            <p key={index}>{paragraph}</p>
                        ))
                    ) : (
                        <p className="text-muted-foreground italic">
                            Full article content is not available. Please visit the original source below.
                        </p>
                    )}
                </div>

                {/* Source Link */}
                {article.url && (
                    <div className="mt-12 pt-8 border-t">
                        <a
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:opacity-90 transition-opacity shadow-sm"
                        >
                            <ExternalLink className="w-4 h-4" />
                            Read full article on original source
                        </a>
                    </div>
                )}
            </div>

            {/* Related Articles */}
            {relatedArticles.length > 0 && (
                <div className="container mx-auto max-w-7xl px-4 md:px-8 mt-24 pt-16 border-t">
                    <h2 className="text-3xl font-bold tracking-tight mb-8 font-heading">Related {article.category} News</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
                        {relatedArticles.map((related) => (
                            <ArticleCard key={related.id} article={related} />
                        ))}
                    </div>
                </div>
            )}
        </article>
    );
}
