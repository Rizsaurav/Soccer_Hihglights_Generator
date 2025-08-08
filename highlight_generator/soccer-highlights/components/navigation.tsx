import Link from "next/link"
import { Home } from "lucide-react"
import { Button } from "@/components/ui/button"

interface NavigationProps {
  currentPage: "soccer" | "cricket"
}

export default function Navigation({ currentPage }: NavigationProps) {
  return (
    <nav className="p-6 bg-white border-b border-gray-100">
      <div className="max-w-6xl mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-gray-900 hover:text-amber-600 transition-colors">
          HighlightPro
        </Link>

        <div className="flex items-center gap-4">
          <Button variant="ghost" className="text-gray-600 hover:text-gray-900 hover:bg-gray-50" asChild>
            <Link href="/">
              <Home className="mr-2 h-4 w-4" /> Home
            </Link>
          </Button>

          {currentPage === "soccer" ? (
            <Button variant="ghost" className="text-gray-600 hover:text-gray-900 hover:bg-gray-50" asChild>
              <Link href="/cricket">🏏 Cricket</Link>
            </Button>
          ) : (
            <Button variant="ghost" className="text-gray-600 hover:text-gray-900 hover:bg-gray-50" asChild>
              <Link href="/soccer">⚽ Soccer</Link>
            </Button>
          )}
        </div>
      </div>
    </nav>
  )
}
