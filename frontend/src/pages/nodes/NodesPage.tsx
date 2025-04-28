import React from "react";

// Simulated dummy data (replace with API later)
const nodes = [
  {
    id: "Node-01",
    status: "Online",
    chunksProcessing: 5,
    type: "Chunker",
    utilization: 70,
  },
  {
    id: "Node-02",
    status: "Online",
    chunksProcessing: 2,
    type: "Processor",
    utilization: 60,
  },
  {
    id: "Node-03",
    status: "Offline",
    chunksProcessing: 0,
    type: "Assembler",
    utilization: 0,
  },
  {
    id: "Node-04",
    status: "Online",
    chunksProcessing: 7,
    type: "Chunker",
    utilization: 90,
  },
];

const totalNodes = nodes.length;
const onlineNodes = nodes.filter((n) => n.status === "Online").length;
const totalChunks = nodes.reduce((sum, node) => sum + node.chunksProcessing, 0);

const getNodeUtilizationColor = (utilization: number) => {
  if (utilization < 50) return "bg-green-200";
  if (utilization < 80) return "bg-yellow-200";
  return "bg-red-200";
};

export default function NodesPage() {
  return (
    <div className="p-4 space-y-4">
      <div>
        <p className="text-xl font-bold">Nodes Summary</p>
      </div>
      {/* Dashboard Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border p-4">
          <p className="text-gray-500 text-sm">Total Nodes</p>
          <h2 className="text-3xl font-bold text-purple-700">{totalNodes}</h2>
        </div>
        <div className="bg-white border p-4">
          <p className="text-gray-500 text-sm">Online Nodes</p>
          <h2 className="text-3xl font-bold text-green-600">{onlineNodes}</h2>
        </div>
        <div className="bg-white border p-4">
          <p className="text-gray-500 text-sm">Chunks Processing</p>
          <h2 className="text-3xl font-bold text-purple-700">{totalChunks}</h2>
        </div>
      </div>

      {/* Nodes Grid */}
      <div>
        <p className="text-xl font-bold">Nodes Status</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {nodes.map((node) => (
          <div key={node.id} className="bg-white p-4 border space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-800">{node.id}</h3>
              <span
                className={`text-xs font-medium px-2 py-1 rounded-full ${
                  node.status === "Online"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}
              >
                {node.status}
              </span>
            </div>

            <div className="space-y-1">
              {/* Node Type */}
              <div className="text-sm text-gray-500">
                <strong>Type:</strong> {node.type}
              </div>

              {/* Chunks Processing */}
              <div className="text-sm text-gray-500">
                <strong>Chunks Processing:</strong>{" "}
                <span className="font-semibold">{node.chunksProcessing}</span>
              </div>
            </div>

            {/* Utilization Chart */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <p className="text-sm text-gray-500">Utilization</p>
                <p className="text-xs text-gray-500 mt-1">
                  {node.utilization}% Utilized
                </p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getNodeUtilizationColor(
                    node.utilization
                  )}`}
                  style={{ width: `${node.utilization}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
