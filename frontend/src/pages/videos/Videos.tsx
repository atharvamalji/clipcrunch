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
      {/* <div>
        <button className="px-4 p-2 bg-purple-600 text-white font-semibold text-sm rounded-full">
          Upload Video
        </button>
      </div> */}

      {/* List of Cards */}
      <div className="grid grid-cols-1 divide-y space-y-4">
        {videos.map((video) => (
          <div key={video.id} className="p-4 bg-white border transition space-y-1 flex space-x-4">
            <div className="w-[5rem] h-full bg-black">

            </div>
            <div className="space-y-2 flex-1">
              <div className="text-lg font-semibold text-black">
                {video.filename}
              </div>
              <hr />
              <div className="text-xs flex space-x-4">
                <div>
                  <strong>Resolution:</strong> {video.resolution}
                </div>
                <div>
                  <strong>Status:</strong> {video.status}
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
            </div>
          </div>
        ))}
        {!videos && ( <div>No videos in database</div> )}
      </div>
    </div>
  );
}
