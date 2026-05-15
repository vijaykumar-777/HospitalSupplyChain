import { useEffect, useState } from 'react';
import { fetchOrders } from '../api';
import { Link, useSearchParams } from 'react-router-dom';
import { format } from 'date-fns';
import { ArrowRight } from 'lucide-react';

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get('status');

  useEffect(() => {
    const loadOrders = async () => {
      try {
        const res = await fetchOrders();
        let data = res.data;
        if (statusFilter) {
          data = data.filter(o => o.status === statusFilter);
        }
        setOrders(data);
      } catch (err) {
        console.error("Failed to load orders", err);
      } finally {
        setLoading(false);
      }
    };
    loadOrders();
  }, [statusFilter]);

  const getStatusStyle = (status) => {
    switch (status) {
      case 'delivered': return 'bg-foreground text-background';
      case 'delayed': return 'border-2 border-foreground font-bold';
      case 'in_transit': return 'border border-foreground';
      default: return 'border border-border-light text-muted-foreground';
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="font-display text-2xl italic text-muted-foreground">Loading…</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <p className="font-data text-[11px] tracking-[0.3em] uppercase text-muted-foreground mb-3">
          Procurement & Logistics
        </p>
        <h1 className="font-display text-6xl font-bold tracking-tight leading-none">
          Orders
        </h1>
        {statusFilter && (
          <p className="font-body text-lg text-muted-foreground mt-3">
            Filtered by: <span className="font-semibold text-foreground uppercase tracking-wider text-sm">{statusFilter}</span>
          </p>
        )}
        <hr className="section-rule mt-6" />
      </div>

      <div className="border-2 border-foreground overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b-2 border-foreground">
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Order ID</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Item</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Supplier</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Qty</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Expected</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Status</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground"></th>
              </tr>
            </thead>
            <tbody>
              {orders.slice(0, 100).map((order) => (
                <tr key={order.order_id} className="border-b border-border-light group hover:bg-foreground hover:text-background transition-colors duration-100">
                  <td className="px-6 py-4 font-data text-xs">{order.order_id.substring(0,8)}</td>
                  <td className="px-6 py-4 font-data text-xs">{order.item_id.substring(0,8)}</td>
                  <td className="px-6 py-4 font-data text-xs">{order.supplier_id.substring(0,8)}</td>
                  <td className="px-6 py-4 font-display text-lg font-bold">{order.quantity}</td>
                  <td className="px-6 py-4 font-body text-sm">{format(new Date(order.expected_delivery_date), 'dd MMM yyyy')}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-block px-3 py-1 font-data text-[10px] tracking-[0.2em] uppercase ${getStatusStyle(order.status)}`}>
                      {order.status}
                    </span>
                    {order.is_emergency_order && (
                      <span className="ml-2 inline-block px-2 py-1 bg-foreground text-background font-data text-[10px] tracking-[0.15em] uppercase font-bold group-hover:bg-background group-hover:text-foreground">
                        SOS
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <Link to={`/orders/${order.order_id}`} className="inline-flex items-center gap-1 font-data text-[10px] tracking-[0.2em] uppercase border-b border-current hover:border-b-2 transition-all duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-3">
                      View <ArrowRight size={10} strokeWidth={1.5} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {orders.length > 100 && (
            <div className="p-4 text-center font-data text-xs tracking-[0.2em] uppercase text-muted-foreground border-t border-border-light">
              Showing first 100 of {orders.length} orders
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
