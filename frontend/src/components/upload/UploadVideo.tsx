"use client";
import React, { useRef, useState } from "react";
import axios from "axios";

interface ProcessingParams {
  chunkSize: number;
  maxNodes: number;
  resolution: string;
  codec: string;
}

export default function UploadVideo() {
  const [file, setFile] = useState<File | null>(null);

  const [params, setParams] = useState<ProcessingParams>({
    chunkSize: 50,
    maxNodes: 5,
    resolution: "1080p",
    codec: "h264",
  });

  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const openFilePicker = () => {
    inputRef.current?.click();
  };

  const resetFile = () => {
    setFile(null);
  };

  // 🛠 Fix input changes
  const handleParamChange = (field: keyof ProcessingParams, value: any) => {
    setParams((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // 🛠 Handle upload
  const handleUpload = async () => {
    if (!file) {
      alert("No file selected.");
      return;
    }

    const formData = new FormData();
    formData.append("video", file);
    formData.append("params", JSON.stringify(params));

    try {
      const response = await axios.post("http://localhost:5000/upload", formData);

      console.log("Upload successful:");
      alert("Upload successful!");
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed. Check console for details.");
    }
  };

  return (
    <div className="flex flex-col space-y-4 p-4 bg-stone-100 h-full">
      <div className="grid grid-cols-6 gap-4">
        <div className="bg-white col-span-6 border p-6 space-y-4">
          <p className="text-lg font-semibold text-gray-700">Upload Video</p>

          {!file ? (
            // Drop Zone
            <div
              className="border-2 border-dashed p-6 flex items-center justify-center cursor-pointer hover:bg-purple-100 transition rounded-md"
              onClick={openFilePicker}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <div className="flex flex-col items-center justify-center">
                <svg
                  className="w-16 h-16 text-purple-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16V4m0 0l-4 4m4-4l4 4M17 8v8m0 0l4-4m-4 4l-4-4"
                  />
                </svg>
                <p className="text-purple-600 font-medium">
                  Drag & Drop your video here
                </p>
                <p className="text-gray-400 text-sm mt-2">or click to select</p>
                <input
                  type="file"
                  accept="video/*"
                  ref={inputRef}
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </div>
            </div>
          ) : (
            // File Info View
            <div className="space-y-4">
              <div className="flex space-x-4">
                <div className="aspect-16/9 border w-30 bg-black"></div>
                <div>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>
                      <span className="font-medium">Filename:</span> {file.name}
                    </p>
                    <p>
                      <span className="font-medium">Size:</span>{" "}
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                    <p>
                      <span className="font-medium">Type:</span> {file.type}
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={resetFile}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 p-2 transition text-xs font-semibold"
              >
                Reupload Video
              </button>
            </div>
          )}
        </div>

        {file && (
          <div className="bg-white col-span-6 border p-4 space-y-4">
            <div>
              <p className="text-lg font-semibold text-gray-700">
                Processing Parameters
              </p>
            </div>

            {/* Input Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Chunk Size */}
              <div className="flex flex-col space-y-1">
                <label className="text-sm text-gray-600 font-medium">
                  Chunk Size (MB)
                </label>
                <input
                  type="number"
                  className="border p-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  value={params.chunkSize}
                  onChange={(e) =>
                    handleParamChange("chunkSize", parseInt(e.target.value))
                  }
                />
              </div>

              {/* Max Nodes */}
              <div className="flex flex-col space-y-1">
                <label className="text-sm text-gray-600 font-medium">
                  Max Nodes
                </label>
                <input
                  type="number"
                  className="border p-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  value={params.maxNodes}
                  onChange={(e) =>
                    handleParamChange("maxNodes", parseInt(e.target.value))
                  }
                />
              </div>

              {/* Target Resolution */}
              <div className="flex flex-col space-y-1">
                <label className="text-sm text-gray-600 font-medium">
                  Target Resolution
                </label>
                <select
                  className="border p-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  value={params.resolution}
                  onChange={(e) =>
                    handleParamChange("resolution", e.target.value)
                  }
                >
                  <option value="1080p">1920x1080 (1080p)</option>
                  <option value="720p">1280x720 (720p)</option>
                  <option value="480p">854x480 (480p)</option>
                </select>
              </div>

              {/* Codec */}
              <div className="flex flex-col space-y-1">
                <label className="text-sm text-gray-600 font-medium">
                  Codec
                </label>
                <select
                  className="border p-2 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  value={params.codec}
                  onChange={(e) => handleParamChange("codec", e.target.value)}
                >
                  <option value="h264">H.264</option>
                  <option value="vp9">VP9</option>
                  <option value="av1">AV1</option>
                </select>
              </div>

              {/* Start Processing Button */}
              <div>
                <button
                  onClick={handleUpload}
                  className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-semibold"
                >
                  Start Video Processing
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
