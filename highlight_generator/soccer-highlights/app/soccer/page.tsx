"use client"

import { Upload, Sparkles, BarChart, Video, Search, GaugeCircle } from "lucide-react"
import VideoUploader from "@/components/video-uploader"
import FeatureCard from "@/components/feature-card"

import Navigation from "@/components/navigation"

export default function SoccerPage() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation currentPage="soccer" />

      {/* Hero Section */}
      <section className="py-24 px-4 bg-gradient-to-b from-amber-50 to-white">
        <div className="max-w-4xl mx-auto text-center">
          <div
            className="w-20 h-20 bg-gradient-to-r from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-8"
            aria-label="Soccer Icon"
          >
            <span className="text-3xl">⚽</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-6 text-gray-900">
            Soccer{" "}
            <span className="bg-gradient-to-r from-amber-500 to-orange-600 bg-clip-text text-transparent">
              Highlights
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Upload your soccer videos and let our AI create the perfect highlights in seconds.
          </p>
        </div>
      </section>

      {/* Upload Section */}
      <section id="upload" className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4 text-gray-900">Upload Your Match</h2>
            <p className="text-xl text-gray-600">Let’s create those golden moments together!</p>
          </div>


          {/* Video Uploader — Common backend connection */}
          <VideoUploader />

          {/* Upload Features */}
          <div className="mt-20 grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Upload className="h-8 w-8 text-amber-600" />}
              title="Easy Upload"
              description="Just drag & drop or paste a video URL. MP4 files are supported perfectly!"
            />
            <FeatureCard
              icon={<Sparkles className="h-8 w-8 text-amber-600" />}
              title="Smart Detection"
              description="Our AI detects goals, fouls, and key moments with precision."
            />
            <FeatureCard
              icon={<BarChart className="h-8 w-8 text-amber-600" />}
              title="Quick Results"
              description="Get your highlight reel within minutes—export-ready and professional."
            />
          </div>
        </div>
      </section>


     
      
    </main>
  )
}
