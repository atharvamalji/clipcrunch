import { createBrowserRouter } from "react-router";

import AppLayout from "./layout/AppLayout";
import UploadVideo from "./components/upload/UploadVideo";
import NodesPage from "./pages/nodes/NodesPage";
import Videos from "./pages/videos/Videos";

const router = createBrowserRouter([
  {
    path: "/",
    Component: AppLayout,
    children: [
      {
        path: "videos",
        Component: Videos,
      },
      {
        path: "upload-video",
        Component: UploadVideo,
      },
      {
        path: "nodes",
        Component: NodesPage,
      },
    ],
  },
  //   {
  //     path: "/processing",
  //     element: <ProcessingPage />,
  //   },
  //   {
  //     path: "/history",
  //     element: <HistoryPage />,
  //   },
  //   {
  //     path: "*",
  //     element: <NotFoundPage />,
  //   },
]);

export default router;
