import { Link } from "react-router";

export default function Sidebar() {
  return (
    <div className="bg-white border-r w-[12rem] flex flex-col py-4 px-4 space-y-4">
      <nav className="flex flex-col space-y-2">
        <Link
          to="/upload-video"
          className="text-gray-700 hover:text-purple-600 font-medium"
        >
          Upload
        </Link>
        <Link
          to="/videos"
          className="text-gray-700 hover:text-purple-600 font-medium"
        >
          Videos
        </Link>

        <Link
          to="/nodes"
          className="text-gray-700 hover:text-purple-600 font-medium"
        >
          Nodes
        </Link>
      </nav>
    </div>
  );
}
