"use client"

import { Upload, Sparkles, BarChart } from "lucide-react"
import VideoUploader from "@/components/video-uploader"
import FeatureCard from "@/components/feature-card"
import Navigation from "@/components/navigation"

export default function CricketPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-green-900 via-orange-800 to-blue-900">
      <Navigation currentPage="cricket" />

      {/* Hero Section */}
      <section className="relative py-20 px-4 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/30 z-0" aria-hidden="true" />
        <div className="z-10 text-center max-w-4xl mx-auto relative">
          <h1 className="text-4xl md:text-6xl font-bold mb-6" aria-label="Cricket Highlights">
            Cricket <span className="text-orange-400">Highlights</span>
          </h1>
          <p className="text-xl md:text-2xl mb-8">
            From <span className="text-orange-400">boundaries</span> to wickets! Upload your cricket videos for instant
            highlights.
          </p>
        </div>

        {/* Floating Cricket Balls */}
        <div className="absolute bottom-10 left-10 w-16 h-16 rounded-full bg-red-600 opacity-20 animate-bounce" />
        <div className="absolute top-20 right-20 w-8 h-8 rounded-full bg-white opacity-10 animate-bounce animation-delay-1000" />
      </section>

      {/* Upload Section */}
      <section id="upload" className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-2 text-green-800">
            Upload Your <span className="text-orange-600">Match</span>
          </h2>
          <p className="text-center text-xl mb-12 text-gray-600">
            Let&apos;s <span className="font-bold">bowl</span> over your audience with amazing highlights!
          </p>

          {/* Shared backend logic – no prop needed */}
          <VideoUploader />

          <div className="mt-16 grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Upload className="h-8 w-8 text-orange-500" />}
              title="Easy Upload"
              description="Just drag & drop or paste a URL. We'll hit it out of the park with MP4 support!"
            />
            <FeatureCard
              icon={<Sparkles className="h-8 w-8 text-orange-500" />}
              title="Smart Detection"
              description="Our AI catches every wicket, boundary, and six! No highlights will be stumped."
            />
            <FeatureCard
              icon={<BarChart className="h-8 w-8 text-orange-500" />}
              title="Quick Delivery"
              description="Faster than a Yorker! Get your highlights delivered in no time."
            />
          </div>
        </div>
      </section>

    </main>
  )
}
