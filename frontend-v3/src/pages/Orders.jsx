import { useEffect, useState } from 'react';
import { fetchOrders } from '../api';
import { Link, useSearchParams } from 'react-router-dom';
import { format } from 'date-fns';
import { ArrowUpRight } from 'lucide-react';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get('status');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetchOrders();
        let data = res.data;
        if (statusFilter) data = data.filter(o => o.status === statusFilter);
        setOrders(data);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, [statusFilter]);

  const statusStyle = (s) => {
    const m = {
      delivered: 'bg-success/15 text-success border-success/20',
      delayed: 'bg-danger/15 text-danger border-danger/20',
      in_transit: 'bg-warning/15 text-warning border-warning/20',
    };
    return m[s] || 'bg-white/5 text-fg-muted border-white/10';
  };

  if (loading) return <div className="flex h-64 items-center justify-center"><div className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6 max-w-[1200px]">
      <div>
        <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-2">Procurement & Logistics</p>
        <h1 className="text-5xl font-semibold tracking-tight bg-gradient-to-b from-white via-white/95 to-white/70 bg-clip-text text-transparent">Orders</h1>
        {statusFilter && <p className="text-sm text-fg-muted mt-2">Filtered: <span className="text-accent font-medium uppercase">{statusFilter}</span></p>}
      </div>

      <div className="rounded-2xl border border-border overflow-hidden bg-gradient-to-b from-white/[0.04] to-transparent">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border">
                {['Order ID','Item','Supplier','Qty','Expected','Status',''].map(h => (
                  <th key={h} className="px-5 py-3 text-[10px] font-mono tracking-widest uppercase text-fg-muted font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {orders.slice(0,100).map(order => (
                <tr key={order.order_id} className="border-b border-border hover:bg-white/[0.03] transition-colors duration-150 group">
                  <td className="px-5 py-3.5 font-mono text-xs text-fg-muted">{order.order_id.substring(0,8)}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-fg-muted">{order.item_id.substring(0,8)}</td>
                  <td className="px-5 py-3.5 font-mono text-xs text-fg-muted">{order.supplier_id.substring(0,8)}</td>
                  <td className="px-5 py-3.5 font-semibold text-fg">{order.quantity}</td>
                  <td className="px-5 py-3.5 text-fg-muted">{format(new Date(order.expected_delivery_date), 'dd MMM yyyy')}</td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-semibold tracking-wider uppercase border ${statusStyle(order.status)}`}>
                      {order.status}
                    </span>
                    {order.is_emergency_order && (
                      <span className="ml-2 inline-block px-2 py-0.5 rounded-full bg-danger/20 text-danger text-[10px] font-bold border border-danger/30">SOS</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <Link to={`/orders/${order.order_id}`} className="inline-flex items-center gap-1 text-xs text-accent hover:text-accent-bright font-medium transition-colors duration-150">
                      View <ArrowUpRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {orders.length > 100 && <div className="p-4 text-center text-xs font-mono text-fg-muted border-t border-border">Showing 100 of {orders.length}</div>}
        </div>
      </div>
    </div>
  );
}
