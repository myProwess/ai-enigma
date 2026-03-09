import Image from "next/image";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { Article } from "@/types";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ArticleCardProps {
    article: Article;
    featured?: boolean;
}

export function ArticleCard({ article, featured = false }: ArticleCardProps) {
    const publishDate = new Date(article.publishDate);
    const formattedDate = formatDistanceToNow(publishDate, { addSuffix: true });

    if (featured) {
        return (
            <Link href={`/article/${article.slug}`} className="group block">
                <Card className="overflow-hidden border-0 shadow-none bg-transparent rounded-none sm:rounded-xl">
                    <div className="relative aspect-video w-full overflow-hidden rounded-xl">
                        <Image
                            src={article.coverImageUrl}
                            alt={article.title}
                            fill
                            className="object-cover transition-transform duration-500 group-hover:scale-105"
                            priority
                            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 75vw, 60vw"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
                        <div className="absolute bottom-0 left-0 p-6 md:p-8 w-full">
                            <div className="flex items-center space-x-3 mb-4">
                                <Badge category={article.category}>{article.category}</Badge>
                                <span className="text-white/80 text-sm font-medium">{formattedDate}</span>
                            </div>
                            <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold text-white mb-3 line-clamp-3 leading-tight tracking-tight">
                                {article.title}
                            </h2>
                            <p className="text-white/80 text-base md:text-lg line-clamp-2 max-w-3xl">
                                {article.excerpt}
                            </p>
                        </div>
                    </div>
                </Card>
            </Link>
        );
    }

    return (
        <Link href={`/article/${article.slug}`} className="group h-full flex block">
            <Card className="overflow-hidden flex flex-col w-full h-full transition-all duration-300 hover:shadow-md dark:hover:border-primary/50 relative border-border/50 bg-card/50 backdrop-blur-sm">
                <div className="relative aspect-[16/10] overflow-hidden">
                    <Image
                        src={article.coverImageUrl}
                        alt={article.title}
                        fill
                        className="object-cover transition-transform duration-500 group-hover:scale-110"
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    />
                </div>
                <CardHeader className="p-5 pb-0 flex-grow">
                    <div className="flex items-center justify-between mb-3">
                        <Badge category={article.category} className="shadow-none">{article.category}</Badge>
                    </div>
                    <h3 className="font-bold text-xl leading-snug line-clamp-3 mb-2 group-hover:text-primary transition-colors">
                        {article.title}
                    </h3>
                    <p className="text-muted-foreground text-sm line-clamp-2 mb-4">
                        {article.excerpt}
                    </p>
                </CardHeader>
                <CardFooter className="p-5 pt-0 mt-auto flex items-center justify-between text-xs text-muted-foreground font-medium">
                    <span className="truncate mr-4">{article.author}</span>
                    <span className="whitespace-nowrap flex-shrink-0">{formattedDate}</span>
                </CardFooter>
            </Card>
        </Link>
    );
}
