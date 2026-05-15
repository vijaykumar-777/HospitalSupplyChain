import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchOrder, fetchOrderPrediction, fetchAlternateSuppliers, fetchSupplier } from '../api';
import { format } from 'date-fns';
import { AlertTriangle, Clock, Truck, ShieldCheck, ArrowLeft, ArrowUpRight } from 'lucide-react';

function InfoRow({ label, value }) {
  return (
    <div>
      <p className="text-[10px] font-mono tracking-widest uppercase text-fg-muted mb-1">{label}</p>
      <p className="text-base font-medium text-fg">{value}</p>
    </div>
  );
}

export default function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [supplier, setSupplier] = useState(null);
  const [alternates, setAlternates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const orderRes = await fetchOrder(id);
        setOrder(orderRes.data);
        const supRes = await fetchSupplier(orderRes.data.supplier_id);
        setSupplier(supRes.data.supplier);
        const predRes = await fetchOrderPrediction(id);
        if (predRes.data.status !== 'pending') setPrediction(predRes.data);
        const altRes = await fetchAlternateSuppliers(orderRes.data.item_id);
        setAlternates(altRes.data.slice(0, 3));
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [id]);

  if (loading) return <div className="flex h-64 items-center justify-center"><div className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" /></div>;
  if (!order) return <p className="text-center py-20 text-fg-muted text-lg">Order not found.</p>;

  const statusStyle = order.status === 'delayed' ? 'bg-danger/15 text-danger border-danger/30' : order.status === 'delivered' ? 'bg-success/15 text-success border-success/30' : 'bg-warning/15 text-warning border-warning/30';

  return (
    <div className="space-y-6 max-w-6xl">
      <Link to="/orders" className="inline-flex items-center gap-1.5 text-xs font-medium text-fg-muted hover:text-fg transition-colors">
        <ArrowLeft size={14} /> Back to Orders
      </Link>

      <div className="flex justify-between items-start">
        <div>
          <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-2">Order Detail</p>
          <h1 className="text-4xl font-semibold tracking-tight bg-gradient-to-b from-white to-white/70 bg-clip-text text-transparent">#{order.order_id.substring(0,8)}</h1>
          <p className="text-sm text-fg-muted mt-1">Placed {format(new Date(order.order_date), 'PPP')}</p>
        </div>
        <span className={`px-3 py-1.5 rounded-full text-[11px] font-semibold tracking-wider uppercase border ${statusStyle}`}>{order.status}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Main — 2 cols */}
        <div className="md:col-span-2 space-y-4">
          {/* Order Info */}
          <div className="p-6 rounded-2xl border border-border bg-gradient-to-b from-white/[0.06] to-white/[0.02]">
            <h2 className="text-base font-semibold mb-4">Order Information</h2>
            <div className="grid grid-cols-2 gap-5">
              <InfoRow label="Item ID" value={order.item_id} />
              <InfoRow label="Quantity" value={order.quantity} />
              <InfoRow label="Expected Delivery" value={format(new Date(order.expected_delivery_date), 'PPP')} />
              <InfoRow label="Emergency" value={order.is_emergency_order ? '🚨 SOS Emergency' : 'Standard'} />
            </div>
          </div>

          {/* AI Prediction */}
          {prediction ? (
            <div className={`p-6 rounded-2xl border ${prediction.is_delayed ? 'border-danger/30 bg-danger/[0.06]' : 'border-success/30 bg-success/[0.06]'}`}>
              <div className="flex items-center gap-2 mb-4">
                {prediction.is_delayed ? <AlertTriangle size={18} className="text-danger" /> : <ShieldCheck size={18} className="text-success" />}
                <h2 className="text-base font-semibold">AI Delay Prediction</h2>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 rounded-xl bg-white/[0.04] border border-border">
                  <span className="text-[10px] font-mono tracking-widest uppercase text-fg-muted">Status</span>
                  <span className={`font-semibold ${prediction.is_delayed ? 'text-danger' : 'text-success'}`}>
                    {prediction.is_delayed ? 'Delay Expected' : 'On Time'}
                  </span>
                </div>
                {prediction.is_delayed && (
                  <>
                    <div className="flex justify-between items-center p-3 rounded-xl bg-white/[0.04] border border-border">
                      <span className="text-[10px] font-mono tracking-widest uppercase text-fg-muted">Extra Days</span>
                      <span className="text-xl font-semibold text-danger">+{prediction.extra_days}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 rounded-xl bg-white/[0.04] border border-border">
                      <span className="text-[10px] font-mono tracking-widest uppercase text-fg-muted">New ETA</span>
                      <span className="font-semibold text-danger">{format(new Date(prediction.new_eta), 'PPP')}</span>
                    </div>
                  </>
                )}
                <div className="p-3 rounded-xl bg-white/[0.04] border border-border">
                  <p className="text-[10px] font-mono tracking-widest uppercase text-fg-muted mb-1.5">AI Reasoning</p>
                  <p className="text-sm text-fg-muted leading-relaxed">{prediction.reason}</p>
                </div>
                <p className="text-right text-[10px] font-mono text-fg-muted/50">Confidence: {Math.round(prediction.confidence * 100)}%</p>
              </div>
            </div>
          ) : (
            <div className="p-6 rounded-2xl border border-border bg-gradient-to-b from-white/[0.04] to-transparent flex flex-col items-center justify-center h-44">
              <Clock size={24} className="text-fg-muted/40 mb-2" />
              <p className="text-sm text-fg-muted">AI prediction pending…</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="p-5 rounded-2xl border border-border bg-gradient-to-b from-white/[0.06] to-white/[0.02]">
            <h2 className="text-sm font-semibold mb-3 flex items-center gap-2"><Truck size={15} className="text-accent" /> Current Supplier</h2>
            {supplier && (
              <div className="space-y-3">
                <p className="font-medium text-fg">{supplier.name}</p>
                <p className="text-xs text-fg-muted">{supplier.city}, {supplier.state}</p>
                <div>
                  <div className="flex justify-between text-[10px] font-mono tracking-widest uppercase text-fg-muted mb-1.5">
                    <span>Reliability</span>
                    <span className="text-fg font-semibold">{Math.round(supplier.reliability_score * 100)}%</span>
                  </div>
                  <div className="w-full h-1 rounded-full bg-white/10">
                    <div className="h-1 rounded-full bg-accent shadow-[0_0_8px_rgba(94,106,210,0.4)]" style={{width: `${supplier.reliability_score * 100}%`}} />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-5 rounded-2xl border border-border bg-gradient-to-b from-white/[0.06] to-white/[0.02]">
            <h2 className="text-sm font-semibold mb-3">Top Alternates</h2>
            <div className="space-y-2.5">
              {alternates.map((alt, idx) => (
                <div key={alt.supplier_id} className="p-3 rounded-xl bg-white/[0.04] border border-border hover:border-border-hover hover:bg-white/[0.06] transition-all duration-200">
                  <div className="flex justify-between items-start">
                    <p className="text-sm font-medium text-fg">{alt.name}</p>
                    <span className="text-[10px] font-mono font-semibold text-accent bg-accent/10 px-2 py-0.5 rounded-full">#{idx+1}</span>
                  </div>
                  <p className="text-[11px] text-fg-muted mt-1">{alt.city} · {alt.avg_lead_days}d lead</p>
                  {alt.is_emergency_certified && <p className="text-[10px] text-success font-semibold mt-1">✓ Emergency Certified</p>}
                </div>
              ))}
            </div>
            <button className="w-full mt-3 bg-white/[0.05] hover:bg-white/[0.08] text-fg text-xs font-medium py-2.5 rounded-lg shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)] transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-1.5">
              Request Reroute <ArrowUpRight size={12} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
