"use client";

interface VideoUploaderProps {
  onFileSelected?: (file: File) => void;
}


import React, { useState, useRef } from "react";
import axios from "axios";
import { Upload, LinkIcon, X, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function VideoUploader({ onFileSelected }: VideoUploaderProps) {

  const [dragActive, setDragActive] = useState(false);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [urlInput, setUrlInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");
  const [progress, setProgress] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file?.type === "video/mp4") {
      setVideoFile(file);
      setError("");
      setSuccess(false);
      setProgress("");
    } else {
      alert("Please upload an MP4 file");
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file?.type === "video/mp4") {
      setVideoFile(file);
      setError("");
      setSuccess(false);
      setProgress("");
    } else {
      alert("Please upload an MP4 file");
    }
  };

  const handleUrlSubmit = () => {
    if (urlInput.trim()) {
      setVideoFile(null);
      setPreviewUrl(urlInput.trim());
      setUrlInput("");
      setError("");
      setSuccess(true);
      setProgress("Preview loaded from URL");
    }
  };

  const clearVideo = () => {
    setVideoFile(null);
    setPreviewUrl("");
    setError("");
    setSuccess(false);
    setProgress("");
  };

  const handleUpload = async () => {
    if (!videoFile) {
      alert("Please select a video first.");
      return;
    }

    const formData = new FormData();
    formData.append("video", videoFile);

    try {
      setLoading(true);
      setError("");
      setSuccess(false);
      setPreviewUrl("");
      setProgress("Starting...");

      // Simulated UI feedback
      setProgress("Breaking down the video...");
      await new Promise((r) => setTimeout(r, 1000));

      setProgress("Checking audio moments...");
      await new Promise((r) => setTimeout(r, 1000));

      setProgress("Finding key scenes...");
      await new Promise((r) => setTimeout(r, 1000));

      setProgress("Stitching the best parts...");
      await new Promise((r) => setTimeout(r, 1000));

      // ✅ Use FastAPI endpoint here
      const response = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        responseType: "blob", // FastAPI returns video as binary blob
      });

      const url = URL.createObjectURL(new Blob([response.data]));
      setPreviewUrl(url);
      setSuccess(true);
      setProgress("✅ All done! Highlight is ready.");

      // Optional: trigger download
      const a = document.createElement("a");
      a.href = url;
      a.download = "highlight.mp4";
      a.click();
      a.remove();
    } catch (err: any) {
      setError(err?.response?.data?.error || "Something went wrong.");
      setProgress("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      {!videoFile && !previewUrl ? (
        <div className="space-y-6">
          <Card
            className={`border-2 border-dashed rounded-lg p-12 text-center ${
              dragActive ? "border-[#FFCC00] bg-[#FFCC00]/10" : "border-gray-300"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="p-4 bg-blue-100 rounded-full">
                <Upload className="h-10 w-10 text-blue-900" />
              </div>
              <h3 className="text-xl font-semibold">Drag & Drop your video here</h3>
              <p className="text-gray-500 max-w-md">
                Drop your MP4 file here or click to browse. Let&apos;s{" "}
                <span className="font-bold">kick off</span> the analysis!
              </p>
              <Button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="bg-blue-900 hover:bg-blue-800"
              >
                Browse Files
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/mp4"
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          </Card>

          <div className="text-center">
            <p className="text-gray-500 mb-4">Or paste a video URL</p>
            <div className="flex max-w-md mx-auto">
              <Input
                type="text"
                placeholder="https://example.com/video.mp4"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="rounded-r-none"
              />
              <Button
                type="button"
                onClick={handleUrlSubmit}
                className="rounded-l-none bg-[#A50044] hover:bg-[#8B0000]"
              >
                <LinkIcon className="h-4 w-4 mr-2" /> Add URL
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <Card className="p-6 relative">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
            onClick={clearVideo}
          >
            <X className="h-5 w-5" />
          </Button>

          <div className="text-center">
            <h3 className="text-xl font-semibold mb-2">{videoFile ? videoFile.name : "Preview"}</h3>
            <p className="text-gray-500 mb-4">
              {videoFile ? `${(videoFile.size / (1024 * 1024)).toFixed(2)} MB` : previewUrl}
            </p>

            <Button
              type="button"
              disabled={loading}
              onClick={handleUpload}
              className="bg-[#FFCC00] hover:bg-[#FFD700] text-blue-900 text-lg px-6 py-5 shadow-lg transform hover:scale-105 transition-transform"
            >
              {loading ? "Working..." : "Generate Highlights"} <Sparkles className="ml-2 h-5 w-5" />
            </Button>

            {progress && <p className="text-blue-600 mt-4">{progress}</p>}
            {previewUrl && (
              <video
                controls
                src={previewUrl}
                className="mx-auto mt-6 rounded shadow max-w-full border border-gray-300"
              />
            )}
            {error && <p className="text-red-600 mt-4">❌ Error: {error}</p>}
            {success && !error && <p className="text-green-600 mt-4">✅ Success! Preview below.</p>}
          </div>
        </Card>
      )}
    </div>
  );
}
