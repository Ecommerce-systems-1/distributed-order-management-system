import { useCallback, useEffect, useRef, useState } from 'react';

type Product = { id: string; name: string; category: string; price: number };
type OrderRow = {
  id: string; customer_id: string; customer_email: string; product_name: string;
  total_amount: number; saga_status: string; created_at: string;
};
type SagaStep = {
  step_number: number; service_name: string; action: string; status: string;
  input_data: any; output_data: any; error_message: string | null;
  started_at: string | null; completed_at: string | null; compensated_at: string | null;
};
type OrderDetail = OrderRow & { quantity: number; unit_price: number; saga_steps: SagaStep[] };

const STEP_STYLE: Record<string, string> = {
  completed: 'bg-emerald-600 border-emerald-600 text-white',
  running: 'bg-indigo-600 border-indigo-600 text-white animate-pulse',
  failed: 'bg-red-600 border-red-600 text-white',
  compensated: 'bg-amber-600 border-amber-600 text-white',
  pending: 'bg-gray-800 border-gray-700 text-gray-500',
};
const STEP_ICON: Record<string, string> = {
  completed: '✓', running: '…', failed: '✗', compensated: '↩', pending: '·',
};
const STATUS_BADGE: Record<string, string> = {
  completed: 'bg-emerald-900 text-emerald-300',
  failed: 'bg-red-900 text-red-300',
  running: 'bg-indigo-900 text-indigo-300',
  saga_started: 'bg-indigo-900 text-indigo-300',
  compensated: 'bg-amber-900 text-amber-300',
};

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [orders, setOrders] = useState<OrderRow[]>([]);
  const [detail, setDetail] = useState<OrderDetail | null>(null);
  const [productId, setProductId] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [failAt, setFailAt] = useState('');
  const [busy, setBusy] = useState(false);
  const pollTimer = useRef<ReturnType<typeof setTimeout>>();

  const loadOrders = useCallback(async () => {
    const d = await fetch('/orders?size=20').then(r => r.json());
    setOrders(d.orders ?? []);
  }, []);

  const loadDetail = useCallback(async (id: string) => {
    const d: OrderDetail = await fetch(`/orders/${id}`).then(r => r.json());
    setDetail(d);
    clearTimeout(pollTimer.current);
    if (d.saga_status === 'running' || d.saga_status === 'saga_started') {
      pollTimer.current = setTimeout(() => loadDetail(id), 700);
    } else {
      loadOrders();
    }
  }, [loadOrders]);

  useEffect(() => {
    fetch('/products').then(r => r.json()).then(d => {
      setProducts(d.products ?? []);
      if (d.products?.length) setProductId(d.products[0].id);
    });
    loadOrders();
    return () => clearTimeout(pollTimer.current);
  }, [loadOrders]);

  const placeOrder = async () => {
    setBusy(true);
    const qs = failAt ? `?fail_at=${failAt}` : '';
    const res = await fetch(`/orders${qs}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_id: 'cust-demo', customer_email: 'demo@example.com',
        product_id: productId, quantity, shipping_address: '1 Demo Street',
      }),
    });
    const data = await res.json();
    setBusy(false);
    if (res.ok) { await loadOrders(); loadDetail(data.order_id); }
  };

  const fmt = (iso: string | null) => (iso ? new Date(iso).toLocaleTimeString() : '—');

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Distributed Order Management System</h1>
        <p className="text-gray-400 mb-8">
          Every order runs a 4-step saga: Inventory, Payment, Fulfillment, Notification.
          Force a failure to watch completed steps compensate in reverse order.
        </p>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h2 className="font-semibold mb-3">Place an order</h2>
              <label className="block text-sm text-gray-400 mb-1">Product</label>
              <select value={productId} onChange={e => setProductId(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm mb-3">
                {products.map(p => (
                  <option key={p.id} value={p.id}>{p.name} — ${p.price.toFixed(2)}</option>
                ))}
              </select>
              <label className="block text-sm text-gray-400 mb-1">Quantity</label>
              <input type="number" min={1} max={10} value={quantity}
                onChange={e => setQuantity(Number(e.target.value) || 1)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm mb-3" />
              <label className="block text-sm text-gray-400 mb-1">Force failure at</label>
              <select value={failAt} onChange={e => setFailAt(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm mb-4">
                <option value="">No failure — saga completes</option>
                <option value="inventory">Inventory (step 1)</option>
                <option value="payment">Payment (step 2)</option>
                <option value="fulfillment">Fulfillment (step 3)</option>
              </select>
              <button onClick={placeOrder} disabled={busy || !productId}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 rounded-lg py-2 font-medium">
                Place order
              </button>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h2 className="font-semibold mb-3">Orders ({orders.length})</h2>
              <div className="space-y-2 max-h-72 overflow-auto">
                {orders.length === 0 && <p className="text-sm text-gray-500">None yet — place one above.</p>}
                {orders.map(o => (
                  <button key={o.id} onClick={() => loadDetail(o.id)}
                    className={`w-full text-left rounded-lg px-3 py-2 border transition-colors ${
                      detail?.id === o.id ? 'border-indigo-500 bg-gray-800' : 'border-gray-800 hover:border-gray-600'
                    }`}>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-mono">{o.id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_BADGE[o.saga_status] ?? 'bg-gray-800 text-gray-400'}`}>
                        {o.saga_status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      {o.product_name} · ${o.total_amount.toFixed(2)}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            {!detail ? (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-10 text-center text-gray-500">
                Place an order or select one to watch its saga run.
              </div>
            ) : (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <div className="flex flex-wrap items-start justify-between gap-3 mb-6">
                  <div>
                    <div className="font-mono text-lg">{detail.id}</div>
                    <div className="text-sm text-gray-400">
                      {detail.product_name} × {detail.quantity} · ${detail.total_amount.toFixed(2)}
                    </div>
                  </div>
                  <span className={`text-sm px-3 py-1 rounded-full ${STATUS_BADGE[detail.saga_status] ?? 'bg-gray-800 text-gray-400'}`}>
                    saga {detail.saga_status}
                  </span>
                </div>

                {/* Saga timeline */}
                <div className="flex items-center mb-8">
                  {detail.saga_steps.map((s, i) => (
                    <div key={s.step_number} className="flex items-center flex-1 last:flex-none">
                      <div className="flex flex-col items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-base font-bold border-2 ${STEP_STYLE[s.status] ?? STEP_STYLE.pending}`}>
                          {STEP_ICON[s.status] ?? '·'}
                        </div>
                        <span className="text-[11px] mt-1.5 whitespace-nowrap text-gray-300">{s.service_name.replace('Service', '')}</span>
                        <span className="text-[10px] text-gray-600">{s.action}</span>
                      </div>
                      {i < detail.saga_steps.length - 1 && (
                        <div className={`h-0.5 flex-1 mx-2 mb-8 ${s.status === 'completed' || s.status === 'compensated' ? 'bg-emerald-600' : 'bg-gray-800'}`} />
                      )}
                    </div>
                  ))}
                </div>

                {/* Step details */}
                <div className="space-y-3">
                  {detail.saga_steps.map(s => (
                    <div key={s.step_number} className="bg-gray-950/60 border border-gray-800 rounded-lg p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                        <div className="font-medium text-sm">
                          {s.step_number}. {s.service_name} <span className="text-gray-500">· {s.action}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          <span>start {fmt(s.started_at)}</span>
                          <span>end {fmt(s.completed_at)}</span>
                          {s.compensated_at && <span className="text-amber-400">compensated {fmt(s.compensated_at)}</span>}
                          <span className={`px-2 py-0.5 rounded-full ${STATUS_BADGE[s.status] ?? 'bg-gray-800 text-gray-400'}`}>
                            {s.status}
                          </span>
                        </div>
                      </div>
                      {s.error_message && <div className="text-xs text-red-400 mb-1">{s.error_message}</div>}
                      {s.output_data && (
                        <pre className="text-xs text-gray-500 overflow-auto">{JSON.stringify(s.output_data)}</pre>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
