import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShoppingCart, Truck, Package, AlertTriangle, Zap } from 'lucide-react';
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
        setActiveDisaster(res.data.active ? res.data.event : null);
      } catch (err) { console.error(err); }
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
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Orders', path: '/orders', icon: ShoppingCart },
    { name: 'Suppliers', path: '/suppliers', icon: Truck },
    { name: 'Inventory', path: '/inventory', icon: Package },
  ];

  return (
    <div className="flex h-screen overflow-hidden bg-base text-fg">
      {/* ── Sidebar ── */}
      <aside className="w-[260px] flex flex-col border-r border-border bg-elevated/60 backdrop-blur-xl relative z-20">
        {/* Brand */}
        <div className="px-5 py-5 flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center shadow-[0_0_12px_rgba(94,106,210,0.4)]">
            <Zap size={14} className="text-white" />
          </div>
          <span className="font-semibold text-[15px] tracking-tight text-fg">HealthChain</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-0.5">
          <p className="px-3 py-2 text-[10px] font-mono tracking-widest uppercase text-fg-muted">Navigation</p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200 group ${
                  isActive
                    ? 'bg-white/[0.08] text-fg shadow-[0_0_0_1px_rgba(255,255,255,0.06)]'
                    : 'text-fg-muted hover:bg-white/[0.05] hover:text-fg'
                }`}
              >
                <Icon size={16} strokeWidth={1.8} className={isActive ? 'text-accent' : 'text-fg-muted group-hover:text-fg-subtle'} />
                {item.name}
              </Link>
            );
          })}

          <div className="my-3 border-t border-border" />
          <p className="px-3 py-2 text-[10px] font-mono tracking-widest uppercase text-fg-muted">Emergency</p>
          <Link
            to="/disaster"
            className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200 group ${
              location.pathname.startsWith('/disaster')
                ? 'bg-accent/15 text-accent-bright shadow-[0_0_0_1px_rgba(94,106,210,0.2)]'
                : 'text-fg-muted hover:bg-white/[0.05] hover:text-fg'
            }`}
          >
            <AlertTriangle size={16} strokeWidth={1.8} className={location.pathname.startsWith('/disaster') ? 'text-accent' : 'text-fg-muted'} />
            Disaster Response
            {activeDisaster && (
              <span className="ml-auto w-2 h-2 rounded-full bg-danger shadow-[0_0_8px_rgba(229,72,77,0.6)] animate-pulse" />
            )}
          </Link>
        </nav>

        <div className="px-5 py-4 border-t border-border">
          <p className="text-[10px] font-mono text-fg-muted/50 tracking-wider">© 2025 HealthChain</p>
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col relative overflow-y-auto bg-[radial-gradient(ellipse_at_top,#0a0a0f_0%,#050506_50%,#020203_100%)]">
        {/* Ambient blob */}
        <div className="pointer-events-none fixed top-[-200px] left-1/2 -translate-x-1/2 w-[900px] h-[600px] rounded-full bg-accent/[0.08] blur-[150px]" style={{ animation: 'float-slow 10s ease-in-out infinite' }} />

        {/* Disaster banner */}
        {activeDisaster && (
          <div className="bg-danger/10 border-b border-danger/20 px-6 py-3 flex justify-between items-center sticky top-0 z-10 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <AlertTriangle size={18} className="text-danger" />
              <div>
                <p className="text-xs font-semibold text-danger tracking-wide uppercase">Active Disaster</p>
                <p className="text-sm text-fg-muted">{activeDisaster.title || activeDisaster.raw_text} — Severity {activeDisaster.severity}/5</p>
              </div>
            </div>
            <Link to="/disaster" className="bg-danger/20 hover:bg-danger/30 text-danger text-xs font-semibold px-4 py-2 rounded-lg transition-colors duration-200">
              View Response →
            </Link>
          </div>
        )}

        <div className="p-8 relative z-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
