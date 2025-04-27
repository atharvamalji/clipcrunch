// // src/components/Layout/LayoutWrapper.tsx
// import React from "react";
// import AppLayout from "./AppLayout";

// interface LayoutWrapperProps {
//   children: React.ReactNode;
//   layout?: "app" | "auth" | "none";
// }

// export default function LayoutWrapper({
//   children,
//   layout = "app",
// }: LayoutWrapperProps) {
//   if (layout === "none") {
//     return <>{children}</>;
//   }
//   // Default: App layout
//   return <AppLayout>{children}</AppLayout>;
// }
