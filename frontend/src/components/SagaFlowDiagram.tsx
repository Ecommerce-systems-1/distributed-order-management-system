const STATUS_COLORS: Record<string, string> = {
  pending:     "border-gray-600 text-gray-400 bg-gray-900",
  running:     "border-yellow-400 text-yellow-300 bg-yellow-900/30 animate-pulse",
  completed:   "border-green-500 text-green-300 bg-green-900/30",
  failed:      "border-red-500 text-red-300 bg-red-900/30",
  compensated: "border-amber-400 text-amber-300 bg-amber-900/30",
};

const STEP_LABELS = [
  { num: 1, service: "InventoryService", action: "reserve()", icon: "📦" },
  { num: 2, service: "PaymentService",   action: "charge()",  icon: "💳" },
  { num: 3, service: "FulfillmentService", action: "route()", icon: "🚚" },
  { num: 4, service: "NotificationService", action: "send()", icon: "📧" },
];

export default function SagaFlowDiagram({ steps }: { steps: any[] }) {
  const stepMap = Object.fromEntries(steps.map(s => [s.step_number, s]));
  return (
    <div className="flex items-center gap-2 flex-wrap justify-center my-6">
      {STEP_LABELS.map((label, i) => {
        const step = stepMap[label.num] ?? {};
        const status = step.status ?? "pending";
        return (
          <div key={label.num} className="flex items-center gap-2">
            <div className={`border-2 rounded-lg p-3 w-40 text-center transition-all ${STATUS_COLORS[status]}`}>
              <div className="text-2xl">{label.icon}</div>
              <div className="text-xs font-bold mt-1">{label.service}</div>
              <div className="text-xs opacity-75">{label.action}</div>
              <div className="text-xs font-semibold mt-2 uppercase tracking-wide">{status}</div>
              {step.completed_at && (
                <div className="text-xs opacity-50 mt-1">
                  {new Date(step.completed_at).toLocaleTimeString()}
                </div>
              )}
            </div>
            {i < STEP_LABELS.length - 1 && (
              <div className="text-gray-500 text-xl font-bold">→</div>
            )}
          </div>
        );
      })}
    </div>
  );
}