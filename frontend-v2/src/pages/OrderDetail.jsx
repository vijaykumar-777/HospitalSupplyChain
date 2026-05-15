import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchOrder, fetchOrderPrediction, fetchAlternateSuppliers, fetchSupplier } from '../api';
import { format } from 'date-fns';
import { AlertTriangle, Clock, Truck, ShieldCheck, ArrowLeft, ArrowRight } from 'lucide-react';

export default function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [supplier, setSupplier] = useState(null);
  const [alternates, setAlternates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const orderRes = await fetchOrder(id);
        setOrder(orderRes.data);

        const supRes = await fetchSupplier(orderRes.data.supplier_id);
        setSupplier(supRes.data.supplier);

        const predRes = await fetchOrderPrediction(id);
        if (predRes.data.status !== 'pending') {
          setPrediction(predRes.data);
        }

        const altRes = await fetchAlternateSuppliers(orderRes.data.item_id);
        setAlternates(altRes.data.slice(0, 3));
      } catch (err) {
        console.error("Failed to load order details", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="font-display text-2xl italic text-muted-foreground">Loading…</p>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="text-center py-20">
        <p className="font-display text-3xl italic text-muted-foreground">Order not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-6xl">
      <Link to="/orders" className="inline-flex items-center gap-2 font-data text-[11px] tracking-[0.2em] uppercase text-muted-foreground hover:text-foreground border-b border-transparent hover:border-foreground transition-all duration-100">
        <ArrowLeft size={14} strokeWidth={1.5} /> Back to Orders
      </Link>

      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <p className="font-data text-[11px] tracking-[0.3em] uppercase text-muted-foreground mb-2">
            Order Detail
          </p>
          <h1 className="font-display text-5xl font-bold tracking-tight leading-none">
            #{order.order_id.substring(0,8)}
          </h1>
          <p className="font-body text-lg text-muted-foreground mt-2">
            Placed on {format(new Date(order.order_date), 'PPP')}
          </p>
        </div>
        <span className={`px-6 py-3 font-data text-[11px] tracking-[0.25em] uppercase font-bold ${
          order.status === 'delayed' ? 'bg-foreground text-background' :
          order.status === 'delivered' ? 'border-2 border-foreground' : 'border border-foreground'
        }`}>
          {order.status}
        </span>
      </div>

      <hr className="section-rule" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-0">
        {/* Main Details — 2 columns */}
        <div className="md:col-span-2 border-2 border-foreground">
          {/* Order Info */}
          <div className="p-8 border-b border-border-light">
            <h2 className="font-display text-xl font-bold tracking-tight mb-6">Order Information</h2>
            <hr className="border-t border-border-light mb-6" />
            <div className="grid grid-cols-2 gap-6">
              {[
                ['Item ID', order.item_id],
                ['Quantity', order.quantity],
                ['Expected Delivery', format(new Date(order.expected_delivery_date), 'PPP')],
                ['Emergency', order.is_emergency_order ? 'SOS Emergency' : 'Standard'],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground mb-1">{label}</p>
                  <p className="font-body text-lg font-medium">{value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* AI Prediction Card */}
          {prediction ? (
            <div className={`p-8 ${prediction.is_delayed ? 'bg-foreground text-background' : ''}`}>
              <div className="flex items-center gap-3 mb-6">
                {prediction.is_delayed
                  ? <AlertTriangle size={20} strokeWidth={1.5} />
                  : <ShieldCheck size={20} strokeWidth={1.5} />
                }
                <h2 className="font-display text-xl font-bold tracking-tight">AI Delay Prediction</h2>
              </div>

              <div className="space-y-4">
                <div className={`flex justify-between items-center p-4 ${prediction.is_delayed ? 'border border-background/20' : 'border border-foreground'}`}>
                  <span className="font-data text-[10px] tracking-[0.2em] uppercase">Status</span>
                  <span className="font-display text-lg font-bold">
                    {prediction.is_delayed ? 'Delay Expected' : 'On Time'}
                  </span>
                </div>

                {prediction.is_delayed && (
                  <>
                    <div className={`flex justify-between items-center p-4 border ${prediction.is_delayed ? 'border-background/20' : 'border-foreground'}`}>
                      <span className="font-data text-[10px] tracking-[0.2em] uppercase">Extra Days</span>
                      <span className="font-display text-2xl font-bold">+{prediction.extra_days}</span>
                    </div>
                    <div className={`flex justify-between items-center p-4 border ${prediction.is_delayed ? 'border-background/20' : 'border-foreground'}`}>
                      <span className="font-data text-[10px] tracking-[0.2em] uppercase">New ETA</span>
                      <span className="font-display text-lg font-bold">{format(new Date(prediction.new_eta), 'PPP')}</span>
                    </div>
                  </>
                )}

                <div className={`p-4 border ${prediction.is_delayed ? 'border-background/20' : 'border-foreground'}`}>
                  <p className="font-data text-[10px] tracking-[0.2em] uppercase mb-2">AI Reasoning</p>
                  <p className="font-body text-sm leading-relaxed italic">{prediction.reason}</p>
                </div>

                <p className={`text-right font-data text-[10px] tracking-[0.15em] ${prediction.is_delayed ? 'text-background/50' : 'text-muted-foreground'}`}>
                  Confidence: {Math.round(prediction.confidence * 100)}%
                </p>
              </div>
            </div>
          ) : (
            <div className="p-8 flex flex-col items-center justify-center h-48">
              <Clock size={28} strokeWidth={1} className="text-muted-foreground mb-3" />
              <p className="font-display text-lg italic text-muted-foreground">Prediction pending…</p>
            </div>
          )}
        </div>

        {/* Sidebar Panel — Suppliers */}
        <div className="border-2 border-foreground border-l-0">
          {/* Current Supplier */}
          <div className="p-6 border-b border-border-light">
            <h2 className="font-display text-lg font-bold tracking-tight mb-4 flex items-center gap-2">
              <Truck size={16} strokeWidth={1.5} /> Current Supplier
            </h2>
            <hr className="border-t border-border-light mb-4" />
            {supplier && (
              <div className="space-y-3">
                <p className="font-body text-lg font-semibold">{supplier.name}</p>
                <p className="font-data text-xs text-muted-foreground">{supplier.city}, {supplier.state}</p>
                <div className="mt-3">
                  <div className="flex justify-between font-data text-[10px] tracking-[0.15em] uppercase text-muted-foreground mb-2">
                    <span>Reliability</span>
                    <span className="font-bold text-foreground">{Math.round(supplier.reliability_score * 100)}%</span>
                  </div>
                  <div className="w-full h-1 bg-border-light">
                    <div className="h-1 bg-foreground" style={{width: `${supplier.reliability_score * 100}%`}} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Alternate Suppliers */}
          <div className="p-6">
            <h2 className="font-display text-lg font-bold tracking-tight mb-4">Top Alternates</h2>
            <hr className="border-t border-border-light mb-4" />
            <div className="space-y-4">
              {alternates.map((alt, idx) => (
                <div key={alt.supplier_id} className="group p-4 border border-foreground hover:bg-foreground hover:text-background transition-colors duration-100">
                  <div className="flex justify-between items-start">
                    <p className="font-body text-sm font-semibold">{alt.name}</p>
                    <span className="font-data text-[10px] tracking-[0.15em] uppercase font-bold bg-foreground text-background px-2 py-1 group-hover:bg-background group-hover:text-foreground">
                      #{idx + 1}
                    </span>
                  </div>
                  <p className="font-data text-[10px] text-muted-foreground group-hover:text-background/60 mt-1">
                    {alt.city} • {alt.avg_lead_days}d lead
                  </p>
                  {alt.is_emergency_certified && (
                    <p className="font-data text-[10px] tracking-[0.15em] uppercase font-bold mt-2">
                      ✓ Emergency Certified
                    </p>
                  )}
                </div>
              ))}
            </div>
            <button className="w-full mt-4 p-3 border-2 border-foreground font-data text-[10px] tracking-[0.2em] uppercase font-medium hover:bg-foreground hover:text-background transition-colors duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-3 flex items-center justify-center gap-2">
              Request Reroute <ArrowRight size={12} strokeWidth={1.5} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
