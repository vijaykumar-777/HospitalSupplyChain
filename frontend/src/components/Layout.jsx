import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShoppingCart, Truck, Package, AlertTriangle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchActiveDisaster } from '../api';

export default function Layout() {
  const location = useLocation();
  const [activeDisaster, setActiveDisaster] = useState(null);

  useEffect(() => {
    // Poll for active disaster every 30s
    const checkDisaster = async () => {
      try {
        const res = await fetchActiveDisaster();
        if (res.data.active) {
          setActiveDisaster(res.data.event);
        } else {
          setActiveDisaster(null);
        }
      } catch (err) {
        console.error("Failed to fetch active disaster", err);
      }
    };
    checkDisaster();
    const interval = setInterval(checkDisaster, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Orders', path: '/orders', icon: <ShoppingCart size={20} /> },
    { name: 'Suppliers', path: '/suppliers', icon: <Truck size={20} /> },
    { name: 'Inventory', path: '/inventory', icon: <Package size={20} /> },
  ];

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md flex flex-col z-20">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <span className="text-blue-600">🏥</span> HealthChain
          </h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || 
                            (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-blue-50 text-blue-700 font-medium' 
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {item.icon}
                {item.name}
              </Link>
            );
          })}
          
          <div className="pt-4 mt-4 border-t border-gray-200">
            <Link
              to="/disaster"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname.startsWith('/disaster')
                  ? 'bg-red-50 text-red-700 font-medium'
                  : 'text-gray-600 hover:bg-red-50 hover:text-red-600'
              }`}
            >
              <AlertTriangle size={20} className={activeDisaster ? "text-red-500 animate-pulse" : ""} />
              Disaster Response
              {activeDisaster && (
                <span className="ml-auto w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
              )}
            </Link>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-y-auto">
        {/* Disaster Alert Banner */}
        {activeDisaster && (
          <div className="bg-red-500 text-white px-6 py-3 flex justify-between items-center shadow-md z-10 sticky top-0">
            <div className="flex items-center gap-3">
              <AlertTriangle size={24} className="animate-pulse" />
              <div>
                <p className="font-bold uppercase tracking-wider text-sm">ACTIVE DISASTER DECLARED</p>
                <p className="text-sm text-red-100">{activeDisaster.title || activeDisaster.raw_text} (Severity: {activeDisaster.severity})</p>
              </div>
            </div>
            <Link to="/disaster" className="bg-white text-red-600 px-4 py-2 rounded-md font-medium text-sm hover:bg-red-50 transition-colors shadow-sm">
              View Response Plan
            </Link>
          </div>
        )}
        
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
