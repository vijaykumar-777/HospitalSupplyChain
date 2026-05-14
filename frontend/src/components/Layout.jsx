import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShoppingCart, Truck, Package, AlertTriangle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchActiveDisaster } from '../api';

export default function Layout() {
  const location = useLocation();
  const [activeDisaster, setActiveDisaster] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const checkDisaster = async () => {
      try {
        const res = await fetchActiveDisaster();
        if (cancelled) return;
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
    window.addEventListener('focus', checkDisaster);
    window.addEventListener('disaster:changed', checkDisaster);

    return () => {
      cancelled = true;
      clearInterval(interval);
      window.removeEventListener('focus', checkDisaster);
      window.removeEventListener('disaster:changed', checkDisaster);
    };
  }, [location.pathname]);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Orders', path: '/orders', icon: <ShoppingCart size={20} /> },
    { name: 'Suppliers', path: '/suppliers', icon: <Truck size={20} /> },
    { name: 'Inventory', path: '/inventory', icon: <Package size={20} /> },
  ];

  return (
    <div className={`flex h-screen overflow-hidden ${activeDisaster ? 'bg-rose-50' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <aside className={`w-64 shadow-md flex flex-col z-20 ${activeDisaster ? 'bg-gradient-to-b from-red-950 via-red-900 to-slate-950 text-white' : 'bg-white'}`}>
        <div className={`p-4 border-b ${activeDisaster ? 'border-red-800' : 'border-gray-200'}`}>
          <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <span className={activeDisaster ? 'text-amber-300' : 'text-blue-600'}>🏥</span>
            <span className={activeDisaster ? 'text-white' : 'text-gray-800'}>HealthChain</span>
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
                    ? activeDisaster
                      ? 'bg-white/10 text-white font-medium'
                      : 'bg-blue-50 text-blue-700 font-medium'
                    : activeDisaster
                      ? 'text-red-100 hover:bg-white/10'
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
                  ? activeDisaster
                    ? 'bg-amber-400 text-red-950 font-medium'
                    : 'bg-red-50 text-red-700 font-medium'
                  : activeDisaster
                    ? 'text-red-100 hover:bg-white/10 hover:text-white'
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
          <div className="bg-gradient-to-r from-red-700 via-red-600 to-orange-600 text-white px-6 py-3 flex justify-between items-center shadow-md z-10 sticky top-0">
            <div className="flex items-center gap-3">
              <AlertTriangle size={24} className="animate-pulse" />
              <div>
                <p className="font-bold uppercase tracking-wider text-sm">ACTIVE DISASTER DECLARED</p>
                <p className="text-sm text-red-100">{activeDisaster.title || activeDisaster.raw_text} (Severity: {activeDisaster.severity})</p>
              </div>
            </div>
            <Link to="/disaster?focus=response-plan" className="bg-white text-red-600 px-4 py-2 rounded-md font-medium text-sm hover:bg-red-50 transition-colors shadow-sm">
              View Response Plan
            </Link>
          </div>
        )}
        
        <div className={`p-8 ${activeDisaster ? 'bg-[radial-gradient(circle_at_top,_rgba(248,113,113,0.08),_transparent_45%)]' : ''}`}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
