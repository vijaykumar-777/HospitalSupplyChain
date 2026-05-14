import { useEffect, useState } from 'react';
import { fetchOrders, fetchInventory, fetchDisasterEvents } from '../api';
import { Activity, PackageX, Truck, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState({
    pendingOrders: 0,
    delayedOrders: 0,
    criticalStock: 0,
    activeDisasters: 0
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
          activeDisasters: events.filter(e => e.is_active).length
        });
      } catch (error) {
        console.error("Dashboard data load failed", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div className="flex h-full items-center justify-center">Loading dashboard...</div>;

  const statCards = [
    { title: 'Pending Orders', value: stats.pendingOrders, icon: <Truck size={24} />, color: 'bg-blue-500', link: '/orders?status=pending' },
    { title: 'Delayed Orders', value: stats.delayedOrders, icon: <AlertCircle size={24} />, color: 'bg-yellow-500', link: '/orders?status=delayed' },
    { title: 'Critical Stock Items', value: stats.criticalStock, icon: <PackageX size={24} />, color: 'bg-red-500', link: '/inventory' },
    { title: 'Active Disasters', value: stats.activeDisasters, icon: <Activity size={24} />, color: 'bg-purple-500', link: '/disaster' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Hospital Overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, idx) => (
          <Link key={idx} to={card.link} className="block transition-transform hover:-translate-y-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className={`h-2 w-full ${card.color}`}></div>
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium text-gray-500">{card.title}</p>
                    <p className="text-3xl font-bold text-gray-800 mt-2">{card.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${card.color.replace('bg-', 'bg-opacity-10 text-')}`}>
                    {card.icon}
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mt-8">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <Link to="/orders" className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition">Place New Order</Link>
          <button className="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition">Export Reports</button>
        </div>
      </div>
    </div>
  );
}
