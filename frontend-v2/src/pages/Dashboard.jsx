import { useEffect, useState } from 'react';
import { fetchOrders, fetchInventory, fetchDisasterEvents } from '../api';
import { Activity, PackageX, Truck, AlertCircle, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState({
    pendingOrders: 0,
    delayedOrders: 0,
    criticalStock: 0,
    activeDisasters: 0,
    totalOrders: 0,
    deliveredOrders: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [ordersRes, invRes, eventsRes] = await Promise.all([
          fetchOrders(),
          fetchInventory(),
          fetchDisasterEvents()
        ]);

        const orders = ordersRes.data;
        const inventory = invRes.data;
        const events = eventsRes.data;

        setStats({
          pendingOrders: orders.filter(o => o.status === 'pending' || o.status === 'in_transit').length,
          delayedOrders: orders.filter(o => o.status === 'delayed').length,
          criticalStock: inventory.filter(i => i.current_stock <= i.reorder_level).length,
          activeDisasters: events.filter(e => e.is_active).length,
          totalOrders: orders.length,
          deliveredOrders: orders.filter(o => o.status === 'delivered').length,
        });
      } catch (error) {
        console.error("Dashboard data load failed", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="font-display text-2xl italic text-muted-foreground">Loading…</p>
      </div>
    );
  }

  const statCards = [
    { title: 'Pending Orders', value: stats.pendingOrders, icon: <Truck size={20} strokeWidth={1.5} />, link: '/orders?status=pending' },
    { title: 'Delayed Orders', value: stats.delayedOrders, icon: <AlertCircle size={20} strokeWidth={1.5} />, link: '/orders?status=delayed' },
    { title: 'Critical Stock', value: stats.criticalStock, icon: <PackageX size={20} strokeWidth={1.5} />, link: '/inventory' },
    { title: 'Active Disasters', value: stats.activeDisasters, icon: <Activity size={20} strokeWidth={1.5} />, link: '/disaster' },
  ];

  return (
    <div className="space-y-12">
      {/* Hero heading */}
      <div>
        <p className="font-data text-[11px] tracking-[0.3em] uppercase text-muted-foreground mb-3">
          Hospital Command Center
        </p>
        <h1 className="font-display text-6xl font-bold tracking-tight leading-none">
          Overview
        </h1>
        <hr className="section-rule mt-6" />
      </div>

      {/* Stat Cards — editorial style */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border-2 border-foreground">
        {statCards.map((card, idx) => (
          <Link
            key={idx}
            to={card.link}
            className={`group p-8 transition-colors duration-100 hover:bg-foreground hover:text-background focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-[-3px] ${
              idx < statCards.length - 1 ? 'border-r border-foreground' : ''
            }`}
          >
            <div className="flex items-center justify-between mb-6">
              <span className="font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground group-hover:text-background/60">
                {card.title}
              </span>
              <span className="group-hover:text-background/60">{card.icon}</span>
            </div>
            <p className="font-display text-5xl font-bold tracking-tight">
              {card.value}
            </p>
            <div className="flex items-center gap-2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-100">
              <span className="font-data text-[10px] tracking-[0.2em] uppercase">View Details</span>
              <ArrowRight size={12} strokeWidth={1.5} />
            </div>
          </Link>
        ))}
      </div>

      {/* Inverted Stats Section — Black background */}
      <div className="bg-foreground text-background p-10 relative overflow-hidden">
        {/* Subtle vertical line texture */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: 'repeating-linear-gradient(90deg, transparent, transparent 1px, #fff 1px, #fff 2px)',
            backgroundSize: '4px 100%',
            opacity: 0.03,
          }}
        />
        <div className="relative z-10">
          <p className="font-data text-[10px] tracking-[0.3em] uppercase text-background/50 mb-6">
            Operational Summary
          </p>
          <div className="grid grid-cols-3 gap-8">
            <div>
              <p className="font-display text-5xl font-bold">{stats.totalOrders}</p>
              <p className="font-body text-sm text-background/60 mt-2">Total Orders Tracked</p>
            </div>
            <div>
              <p className="font-display text-5xl font-bold">{stats.deliveredOrders}</p>
              <p className="font-body text-sm text-background/60 mt-2">Successfully Delivered</p>
            </div>
            <div>
              <p className="font-display text-5xl font-bold">
                {stats.totalOrders > 0 ? Math.round((stats.deliveredOrders / stats.totalOrders) * 100) : 0}%
              </p>
              <p className="font-body text-sm text-background/60 mt-2">Fulfillment Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="border-2 border-foreground p-8">
        <h2 className="font-display text-2xl font-bold tracking-tight mb-6">Quick Actions</h2>
        <hr className="section-rule--thin border-t border-border-light mb-6" />
        <div className="flex gap-4">
          <Link
            to="/orders"
            className="bg-foreground text-background px-8 py-4 font-data text-xs tracking-[0.2em] uppercase font-medium hover:bg-background hover:text-foreground border-2 border-foreground transition-colors duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-3"
          >
            Place New Order →
          </Link>
          <button className="bg-background text-foreground px-8 py-4 font-data text-xs tracking-[0.2em] uppercase font-medium border-2 border-foreground hover:bg-foreground hover:text-background transition-colors duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-3">
            Export Reports
          </button>
        </div>
      </div>
    </div>
  );
}
