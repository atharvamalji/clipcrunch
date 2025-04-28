import React, { useEffect, useState } from "react";
import axios from "axios";

// Define interfaces for the video data structure
interface Video {
  id: number;
  filename: string;
  stored_filename: string;
  status: string;
  uploader_ip: string | null;
  size: number;
  resolution: string;
  video_bitrate: string;
  audio_bitrate: string;
  crf_value: string;
  preset: string;
  video_codec: string;
  audio_codec: string;
  created_at: string;
  updated_at: string | null;
  totalChunks: number; // New field for total chunks
  processedChunks: number; // New field for processed chunks
}

export default function Videos() {
  // State to hold the videos data, loading, and error
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch all videos from the API
  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const response = await axios.get<Video[]>(
          "http://localhost:5000/api/videos"
        );
        setVideos(response.data);
        setLoading(false);
      } catch (err) {
        setError("Error fetching videos");
        setLoading(false);
      }
    };

    fetchVideos();
  }, []);

  if (loading) return <div>Loading videos...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="p-4 flex flex-col gap-2 bg-stone-50 h-full">
      <div>
        <p className="text-2xl font-bold">Videos</p>
      </div>

      {/* List of Cards */}
      <div className="grid grid-cols-1 divide-y space-y-4">
        {videos.map((video) => {
          const completionPercentage =
            video.totalChunks === 0
              ? 0
              : (video.processedChunks / video.totalChunks) * 100;

          return (
            <div
              key={video.id}
              className={`p-4 bg-white border transition space-y-1 flex space-x-4 rounded-lg ${
                video.status === "processing"
                  ? "border-yellow-500"
                  : video.status === "processed"
                  ? "border-green-500"
                  : "border-gray-300"
              }`}
            >
              <div className="w-[5rem] h-full bg-black"></div>
              <div className="space-y-2 flex-1">
                <div className="text-base font-semibold text-black">
                  {video.filename}
                </div>
                <div className="text-xs flex space-x-4">
                  <div>
                    <strong>Status:</strong>{" "}
                    <span
                      className={`px-2 py-1 rounded-full font-medium ${
                        video.status === "uploaded"
                          ? "bg-blue-100 text-blue-700"
                          : video.status === "processing"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      }`}
                    >
                      {video.status}
                    </span>
                  </div>
                  <div>
                    <strong>Resolution:</strong> {video.resolution}
                  </div>

                  <div>
                    <strong>Video Codec:</strong> {video.video_codec}
                  </div>
                  <div>
                    <strong>Audio Codec:</strong> {video.audio_codec}
                  </div>
                  <div>
                    <strong>Size:</strong>{" "}
                    {(video.size / (1024 * 1024)).toFixed(2)} MB
                  </div>
                </div>
                {video.status === "processing" && (
                  <div>
                    <div>
                      <strong>Total Chunks:</strong> {video.totalChunks}
                    </div>
                    <div>
                      <strong>Processed Chunks:</strong> {video.processedChunks}
                    </div>
                  </div>
                )}

                {/* Progress Bar and Dynamic UI */}
                {video.status === "processing" && (
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      Processing Completion: {completionPercentage.toFixed(2)}%
                    </p>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-yellow-600"
                        style={{ width: `${completionPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* {video.status === "uploaded" && (
                  <div className="mt-4">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-md">
                      Start Processing
                    </button>
                  </div>
                )} */}

                {video.status === "processed" && (
                  <div className="mt-4 text-green-600">
                    <p className="text-sm">Video processing is complete.</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {!videos.length && <div>No videos in the database</div>}
      </div>
    </div>
  );
}
