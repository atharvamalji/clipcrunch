export default function NodesPage() {
  // Simulated dummy data (replace with API later)
  const nodes = [
    { id: "Node-01", status: "Online", chunksProcessing: 5 },
    { id: "Node-02", status: "Online", chunksProcessing: 2 },
    { id: "Node-03", status: "Offline", chunksProcessing: 0 },
    { id: "Node-04", status: "Online", chunksProcessing: 7 },
  ];

  const totalNodes = nodes.length;
  const onlineNodes = nodes.filter((n) => n.status === "Online").length;
  const totalChunks = nodes.reduce(
    (sum, node) => sum + node.chunksProcessing,
    0
  );

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
      <div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {nodes.map((node) => (
            <div
              key={node.id}
              className="bg-white p-6 rounded-xl shadow space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">
                  {node.id}
                </h3>
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
              <div className="text-sm text-gray-500">
                Chunks Processing:{" "}
                <span className="font-semibold text-gray-700">
                  {node.chunksProcessing}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
