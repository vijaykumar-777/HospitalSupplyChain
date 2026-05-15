import { useEffect, useState } from 'react';
import { fetchInventory } from '../api';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try { const res = await fetchInventory(); setInventory(res.data); }
      catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  if (loading) return <div className="flex h-64 items-center justify-center"><div className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" /></div>;

  const criticalCount = inventory.filter(i => i.current_stock <= i.reorder_level).length;

  return (
    <div className="space-y-6 max-w-[1200px]">
      <div>
        <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-2">Warehouse & Stock</p>
        <h1 className="text-5xl font-semibold tracking-tight bg-gradient-to-b from-white via-white/95 to-white/70 bg-clip-text text-transparent">Inventory</h1>
      </div>

      {criticalCount > 0 && (
        <div className="flex items-center gap-3 p-4 rounded-2xl border border-danger/20 bg-danger/[0.06]">
          <AlertCircle size={18} className="text-danger shrink-0" />
          <div>
            <p className="text-sm font-semibold text-danger">{criticalCount} items below reorder level</p>
            <p className="text-xs text-fg-muted">Immediate procurement action required.</p>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-border overflow-hidden bg-gradient-to-b from-white/[0.04] to-transparent">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border">
                {['Item','Stock','Reorder Lvl','Days Left','Status',''].map(h => (
                  <th key={h} className="px-5 py-3 text-[10px] font-mono tracking-widest uppercase text-fg-muted font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {inventory.slice(0,100).map(inv => {
                const isCritical = inv.current_stock <= inv.reorder_level;
                const dailyUse = inv.daily_consumption_normal || 0;
                const daysRemaining = dailyUse > 0 ? Math.round(inv.current_stock / dailyUse) : 0;
                return (
                  <tr key={inv.item_id} className={`border-b border-border transition-colors duration-150 ${isCritical ? 'bg-danger/[0.04]' : 'hover:bg-white/[0.03]'}`}>
                    <td className="px-5 py-3.5 font-mono text-xs text-fg-muted">{inv.item_id.substring(0,8)}</td>
                    <td className="px-5 py-3.5 font-semibold text-fg text-base">{inv.current_stock}</td>
                    <td className="px-5 py-3.5 text-fg-muted">{inv.reorder_level}</td>
                    <td className={`px-5 py-3.5 font-semibold ${daysRemaining < 7 ? 'text-danger' : 'text-fg'}`}>{daysRemaining}d</td>
                    <td className="px-5 py-3.5">
                      {isCritical ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold tracking-wider uppercase text-danger">
                          <AlertCircle size={13} /> Reorder
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold tracking-wider uppercase text-success">
                          <CheckCircle size={13} /> Healthy
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <button className="text-xs text-accent hover:text-accent-bright font-medium transition-colors">Order</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
