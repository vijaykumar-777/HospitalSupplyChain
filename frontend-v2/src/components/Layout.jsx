import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShoppingCart, Truck, Package, AlertTriangle, ArrowRight } from 'lucide-react';
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
    { name: 'Overview', path: '/', icon: <LayoutDashboard size={18} strokeWidth={1.5} /> },
    { name: 'Orders', path: '/orders', icon: <ShoppingCart size={18} strokeWidth={1.5} /> },
    { name: 'Suppliers', path: '/suppliers', icon: <Truck size={18} strokeWidth={1.5} /> },
    { name: 'Inventory', path: '/inventory', icon: <Package size={18} strokeWidth={1.5} /> },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* ── Sidebar ── */}
      <aside className="w-72 border-r-4 border-foreground flex flex-col bg-background relative">
        {/* Subtle horizontal line texture */}
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 1px, #000 1px, #000 2px)',
            backgroundSize: '100% 4px',
            opacity: 0.015,
          }}
        />

        {/* Brand */}
        <div className="p-6 border-b-2 border-foreground relative z-10">
          <h1 className="font-display text-2xl font-bold tracking-tight">
            Health<span className="italic">Chain</span>
          </h1>
          <p className="font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground mt-1">
            Supply Intelligence
          </p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 relative z-10">
          <p className="font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground px-4 mb-3">
            Navigation
          </p>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path ||
                            (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 font-body text-sm transition-colors duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-3 ${
                  isActive
                    ? 'bg-foreground text-background font-semibold'
                    : 'text-foreground hover:bg-foreground hover:text-background'
                }`}
              >
                {item.icon}
                <span className="tracking-wide">{item.name}</span>
                {isActive && <ArrowRight size={14} strokeWidth={1.5} className="ml-auto" />}
              </Link>
            );
          })}

          {/* Disaster Link — separated by a thick rule */}
          <hr className="section-rule my-4" />
          <p className="font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground px-4 mb-3">
            Emergency
          </p>
          <Link
            to="/disaster"
            className={`flex items-center gap-3 px-4 py-3 font-body text-sm border-2 transition-colors duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-foreground focus-visible:outline-offset-3 ${
              location.pathname.startsWith('/disaster')
                ? 'bg-foreground text-background border-foreground font-semibold'
                : 'border-foreground text-foreground hover:bg-foreground hover:text-background'
            }`}
          >
            <AlertTriangle size={18} strokeWidth={1.5} />
            <span className="tracking-wide">Disaster Response</span>
            {activeDisaster && (
              <span className="ml-auto w-2.5 h-2.5 bg-foreground border border-background animate-pulse" />
            )}
          </Link>
        </nav>

        {/* Footer */}
        <div className="p-6 border-t border-border-light relative z-10">
          <p className="font-data text-[10px] tracking-[0.2em] text-muted-foreground uppercase">
            © 2025 HealthChain
          </p>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className="flex-1 flex flex-col relative overflow-y-auto">
        {/* Disaster Alert Banner — Inverted Black */}
        {activeDisaster && (
          <div className="bg-foreground text-background px-8 py-4 flex justify-between items-center sticky top-0 z-10 border-b-4 border-background">
            <div className="flex items-center gap-4">
              <AlertTriangle size={22} strokeWidth={1.5} />
              <div>
                <p className="font-display font-bold text-sm tracking-[0.15em] uppercase">
                  Active Disaster Declared
                </p>
                <p className="font-body text-sm opacity-80 mt-0.5">
                  {activeDisaster.title || activeDisaster.raw_text} — Severity {activeDisaster.severity}/5
                </p>
              </div>
            </div>
            <Link
              to="/disaster?focus=response-plan"
              className="bg-background text-foreground px-6 py-2.5 font-data text-xs tracking-[0.2em] uppercase font-medium hover:bg-muted transition-colors duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-background focus-visible:outline-offset-3"
            >
              View Response →
            </Link>
          </div>
        )}

        <div className="p-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
