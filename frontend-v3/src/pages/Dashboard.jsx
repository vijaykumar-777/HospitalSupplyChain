import { useEffect, useState } from 'react';
import { fetchOrders, fetchInventory, fetchDisasterEvents } from '../api';
import { Activity, PackageX, Truck, AlertCircle, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

function StatCard({ title, value, icon: Icon, link, color = 'accent' }) {
  const colorMap = {
    accent: { bg: 'bg-accent/10', text: 'text-accent', glow: 'shadow-[0_0_20px_rgba(94,106,210,0.15)]' },
    danger: { bg: 'bg-danger/10', text: 'text-danger', glow: 'shadow-[0_0_20px_rgba(229,72,77,0.15)]' },
    warning: { bg: 'bg-warning/10', text: 'text-warning', glow: 'shadow-[0_0_20px_rgba(245,166,35,0.15)]' },
    success: { bg: 'bg-success/10', text: 'text-success', glow: 'shadow-[0_0_20px_rgba(48,164,108,0.15)]' },
  };
  const c = colorMap[color];

  return (
    <Link to={link} className="group relative p-6 rounded-2xl border border-border bg-gradient-to-b from-white/[0.06] to-white/[0.02] hover:border-border-hover hover:shadow-[0_8px_40px_rgba(0,0,0,0.4),0_0_60px_rgba(94,106,210,0.08)] transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-9 h-9 rounded-xl ${c.bg} flex items-center justify-center ${c.glow}`}>
          <Icon size={18} strokeWidth={1.8} className={c.text} />
        </div>
        <ArrowUpRight size={14} className="text-fg-muted opacity-0 group-hover:opacity-100 transition-opacity duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
      </div>
      <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-1">{title}</p>
      <p className="text-4xl font-semibold tracking-tight bg-gradient-to-b from-white via-white/95 to-white/70 bg-clip-text text-transparent">{value}</p>
    </Link>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState({ pendingOrders: 0, delayedOrders: 0, criticalStock: 0, activeDisasters: 0, totalOrders: 0, deliveredOrders: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [o, i, e] = await Promise.all([fetchOrders(), fetchInventory(), fetchDisasterEvents()]);
        const orders = o.data, inv = i.data, events = e.data;
        setStats({
          pendingOrders: orders.filter(x => x.status === 'pending' || x.status === 'in_transit').length,
          delayedOrders: orders.filter(x => x.status === 'delayed').length,
          criticalStock: inv.filter(x => x.current_stock <= x.reorder_level).length,
          activeDisasters: events.filter(x => x.is_active).length,
          totalOrders: orders.length,
          deliveredOrders: orders.filter(x => x.status === 'delivered').length,
        });
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  if (loading) return (
    <div className="flex h-full items-center justify-center">
      <div className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
    </div>
  );

  const rate = stats.totalOrders > 0 ? Math.round((stats.deliveredOrders / stats.totalOrders) * 100) : 0;

  return (
    <div className="space-y-8 max-w-[1200px]">
      {/* Header */}
      <div>
        <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-2">Hospital Command Center</p>
        <h1 className="text-5xl font-semibold tracking-tight bg-gradient-to-b from-white via-white/95 to-white/70 bg-clip-text text-transparent">Overview</h1>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Pending Orders" value={stats.pendingOrders} icon={Truck} link="/orders?status=pending" color="accent" />
        <StatCard title="Delayed Orders" value={stats.delayedOrders} icon={AlertCircle} link="/orders?status=delayed" color="warning" />
        <StatCard title="Critical Stock" value={stats.criticalStock} icon={PackageX} link="/inventory" color="danger" />
        <StatCard title="Active Disasters" value={stats.activeDisasters} icon={Activity} link="/disaster" color={stats.activeDisasters > 0 ? 'danger' : 'success'} />
      </div>

      {/* Operational Summary — bento */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total Orders', val: stats.totalOrders },
          { label: 'Delivered', val: stats.deliveredOrders },
          { label: 'Fulfillment Rate', val: `${rate}%` },
        ].map(item => (
          <div key={item.label} className="p-6 rounded-2xl border border-border bg-gradient-to-b from-white/[0.04] to-transparent">
            <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-2">{item.label}</p>
            <p className="text-3xl font-semibold tracking-tight bg-gradient-to-b from-white to-white/70 bg-clip-text text-transparent">{item.val}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="p-6 rounded-2xl border border-border bg-gradient-to-b from-white/[0.04] to-transparent">
        <h2 className="text-lg font-semibold tracking-tight mb-4">Quick Actions</h2>
        <div className="flex gap-3">
          <Link to="/orders" className="bg-accent hover:bg-accent-bright text-white text-sm font-medium px-5 py-2.5 rounded-lg shadow-[0_0_0_1px_rgba(94,106,210,0.5),0_4px_12px_rgba(94,106,210,0.3),inset_0_1px_0_0_rgba(255,255,255,0.2)] hover:shadow-[0_0_0_1px_rgba(94,106,210,0.6),0_8px_20px_rgba(94,106,210,0.4),inset_0_1px_0_0_rgba(255,255,255,0.2)] transition-all duration-200 active:scale-[0.98]">
            Place New Order →
          </Link>
          <button className="bg-white/[0.05] hover:bg-white/[0.08] text-fg text-sm font-medium px-5 py-2.5 rounded-lg shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)] transition-all duration-200 active:scale-[0.98]">
            Export Reports
          </button>
        </div>
      </div>
    </div>
  );
}
