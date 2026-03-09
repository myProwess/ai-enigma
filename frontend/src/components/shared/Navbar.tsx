import Link from "next/link";
import { Search } from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

const categories = [
    { name: "Technology", href: "/category/technology" },
    { name: "Business", href: "/category/business" },
    { name: "Sports", href: "/category/sports" },
    { name: "Politics", href: "/category/politics" },
];

export function Navbar() {
    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-16 items-center px-4 md:px-8 mx-auto max-w-7xl">
                <div className="mr-8 hidden md:flex">
                    <Link href="/" className="flex items-center space-x-2">
                        <span className="hidden font-bold sm:inline-block text-xl tracking-tight">
                            AI <span className="text-primary">Enigma</span>
                        </span>
                    </Link>
                </div>

                {/* Mobile Logo */}
                <div className="flex flex-1 md:hidden">
                    <Link href="/" className="font-bold text-lg tracking-tight">
                        AI <span className="text-primary">Enigma</span>
                    </Link>
                </div>

                {/* Desktop Categories */}
                <nav className="hidden md:flex items-center space-x-6 text-sm font-medium flex-1">
                    {categories.map((category) => (
                        <Link
                            key={category.name}
                            href={category.href}
                            className="transition-colors hover:text-foreground/80 text-foreground/60"
                        >
                            {category.name}
                        </Link>
                    ))}
                </nav>

                {/* Right Actions */}
                <div className="flex items-center justify-end space-x-4">
                    <nav className="flex items-center space-x-2">
                        <button className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-9 w-9 px-0">
                            <Search className="h-4 w-4" />
                            <span className="sr-only">Search</span>
                        </button>
                        <ThemeToggle />
                    </nav>
                </div>
            </div>
        </header>
    );
}
