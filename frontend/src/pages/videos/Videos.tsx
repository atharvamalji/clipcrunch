import React, { useEffect, useState, useRef } from "react";
import axios from "axios";

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
  totalChunks: number;
  processedChunks: number;
  download_url: string | null;
}

export default function Videos() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const lastVideosRef = useRef<Video[]>([]);

  // Initial load
  useEffect(() => {
    (async () => {
      try {
        const { data } = await axios.get<Video[]>(
          "http://127.0.0.1:5000/api/videos"
        );
        setVideos(data);
        lastVideosRef.current = data;
      } catch {
        setError("Error fetching videos");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Polling – stops when last video processed
  useEffect(() => {
    if (loading || error) return;
    const interval = setInterval(async () => {
      if (!lastVideosRef.current.length) return;
      const last = lastVideosRef.current[lastVideosRef.current.length - 1];
      if (last.status === "processed") {
        clearInterval(interval);
        return;
      }
      try {
        const { data: newVideos } = await axios.get<Video[]>(
          "http://127.0.0.1:5000/api/videos"
        );
        const changed = newVideos.some((nv) => {
          const ov = lastVideosRef.current.find((v) => v.id === nv.id);
          return !ov || ov.status !== nv.status;
        });
        if (changed) {
          setVideos(newVideos);
          lastVideosRef.current = newVideos;
        }
      } catch {
        /* ignore */
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [loading, error]);

  // Download handler
  const handleDownload = async (video: Video) => {
    if (!video.download_url) return;
    try {
      const response = await axios.get(`http://127.0.0.1:5000${video.download_url}`, {
        responseType: "blob",
      });
      // Create a blob link to download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = video.filename;              // use original filename
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed", err);
    }
  };

  if (loading) return <div>Loading videos...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="p-4 flex flex-col gap-2 bg-stone-50 h-full">
      <div>
        <p className="text-2xl font-bold">Videos</p>
      </div>

      <div className="grid grid-cols-1 divide-y space-y-4">
        {videos.map((video) => {
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
                {/* Clickable title invokes download API */}
                <div className="text-base font-semibold text-black">
                  {video.download_url ? (
                    <button
                      onClick={() => handleDownload(video)}
                      className="text-blue-600 hover:underline"
                    >
                      {video.filename}
                    </button>
                  ) : (
                    video.filename
                  )}
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

                {video.status === "processed" && (
                  <div className="mt-4 text-green-600">
                    <p className="text-sm">
                      Video processing is complete. Click title to download.
                    </p>
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
