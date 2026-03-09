import Link from "next/link";
import { ThemeToggle } from "./ThemeToggle";
import { getUniqueCategories } from "@/lib/data";

export async function Navbar() {
    const categories = await getUniqueCategories();

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-16 items-center px-4 md:px-8 mx-auto max-w-7xl">
                <div className="mr-8 hidden md:flex">
                    <Link href="/" className="flex items-center space-x-2">
                        <span className="hidden font-bold sm:inline-block text-xl tracking-tight font-heading">
                            AI <span className="text-primary">Enigma</span>
                        </span>
                    </Link>
                </div>

                {/* Mobile Logo */}
                <div className="flex flex-1 md:hidden">
                    <Link href="/" className="font-bold text-lg tracking-tight font-heading">
                        AI <span className="text-primary">Enigma</span>
                    </Link>
                </div>

                {/* Desktop Categories — dynamically generated from data */}
                <nav className="hidden md:flex items-center space-x-6 text-sm font-medium flex-1">
                    {categories.map((cat) => (
                        <Link
                            key={cat}
                            href={`/category/${cat.toLowerCase()}`}
                            className="transition-colors hover:text-foreground/80 text-foreground/60"
                        >
                            {cat}
                        </Link>
                    ))}
                </nav>

                {/* Right Actions */}
                <div className="flex items-center justify-end space-x-4">
                    <nav className="flex items-center space-x-2">
                        <ThemeToggle />
                    </nav>
                </div>
            </div>
        </header>
    );
}
