import Link from "next/link";

export function Footer() {
    return (
        <footer className="w-full border-t bg-background">
            <div className="container px-4 md:px-8 mx-auto max-w-7xl py-10">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div className="space-y-3">
                        <h3 className="font-bold text-lg tracking-tight">
                            NewsRepo<span className="text-primary">AI</span>
                        </h3>
                        <p className="text-sm text-muted-foreground w-full max-w-xs">
                            A modern, intelligent news platform delivering the most critical stories from around the globe.
                        </p>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4 text-sm uppercase tracking-wider">Categories</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><Link href="/category/technology" className="hover:text-foreground transition-colors">Technology</Link></li>
                            <li><Link href="/category/business" className="hover:text-foreground transition-colors">Business</Link></li>
                            <li><Link href="/category/sports" className="hover:text-foreground transition-colors">Sports</Link></li>
                            <li><Link href="/category/politics" className="hover:text-foreground transition-colors">Politics</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4 text-sm uppercase tracking-wider">Company</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><Link href="#" className="hover:text-foreground transition-colors">About Us</Link></li>
                            <li><Link href="#" className="hover:text-foreground transition-colors">Careers</Link></li>
                            <li><Link href="#" className="hover:text-foreground transition-colors">Editorial Guidelines</Link></li>
                            <li><Link href="#" className="hover:text-foreground transition-colors">Contact</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold mb-4 text-sm uppercase tracking-wider">Legal</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><Link href="#" className="hover:text-foreground transition-colors">Privacy Policy</Link></li>
                            <li><Link href="#" className="hover:text-foreground transition-colors">Terms of Service</Link></li>
                            <li><Link href="#" className="hover:text-foreground transition-colors">Cookie Policy</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t mt-10 pt-6 flex flex-col md:flex-row justify-between items-center text-xs text-muted-foreground">
                    <p>© {new Date().getFullYear()} AI Enigma. All rights reserved.</p>
                    <div className="flex space-x-4 mt-4 md:mt-0">
                        <Link href="#" className="hover:text-foreground transition-colors">Twitter</Link>
                        <Link href="#" className="hover:text-foreground transition-colors">LinkedIn</Link>
                        <Link href="#" className="hover:text-foreground transition-colors">Facebook</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
