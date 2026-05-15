import { useEffect, useState } from 'react';
import { fetchInventory } from '../api';
import { AlertCircle, CheckCircle } from 'lucide-react';

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetchInventory();
        setInventory(res.data);
      } catch (err) {
        console.error("Failed to load inventory", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="font-display text-2xl italic text-muted-foreground">Loading…</p>
      </div>
    );
  }

  const criticalCount = inventory.filter(i => i.current_stock <= i.reorder_level).length;

  return (
    <div className="space-y-8">
      <div>
        <p className="font-data text-[11px] tracking-[0.3em] uppercase text-muted-foreground mb-3">
          Warehouse & Stock
        </p>
        <h1 className="font-display text-6xl font-bold tracking-tight leading-none">
          Inventory
        </h1>
        <hr className="section-rule mt-6" />
      </div>

      {/* Critical Alert Banner */}
      {criticalCount > 0 && (
        <div className="bg-foreground text-background p-6 flex items-center gap-4">
          <AlertCircle size={22} strokeWidth={1.5} />
          <div>
            <p className="font-display text-lg font-bold">{criticalCount} items below reorder level</p>
            <p className="font-body text-sm opacity-70">Immediate procurement action required.</p>
          </div>
        </div>
      )}

      <div className="border-2 border-foreground overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b-2 border-foreground">
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Item</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Stock</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Reorder Lvl</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Days Left</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground">Status</th>
                <th className="px-6 py-4 font-data text-[10px] tracking-[0.25em] uppercase text-muted-foreground"></th>
              </tr>
            </thead>
            <tbody>
              {inventory.slice(0, 100).map((inv) => {
                const isCritical = inv.current_stock <= inv.reorder_level;
                const dailyUse = inv.daily_consumption_normal || 0;
                const daysRemaining = dailyUse > 0 ? Math.round(inv.current_stock / dailyUse) : 0;

                return (
                  <tr
                    key={inv.item_id}
                    className={`border-b border-border-light transition-colors duration-100 ${
                      isCritical
                        ? 'bg-foreground text-background'
                        : 'hover:bg-foreground hover:text-background'
                    }`}
                  >
                    <td className="px-6 py-4 font-data text-xs">{inv.item_id.substring(0,8)}</td>
                    <td className="px-6 py-4 font-display text-xl font-bold">{inv.current_stock}</td>
                    <td className="px-6 py-4 font-body">{inv.reorder_level}</td>
                    <td className={`px-6 py-4 font-display text-lg font-bold ${
                      daysRemaining < 7 && !isCritical ? 'text-foreground' : ''
                    }`}>
                      {daysRemaining}d
                    </td>
                    <td className="px-6 py-4">
                      {isCritical ? (
                        <span className="inline-flex items-center gap-1 font-data text-[10px] tracking-[0.15em] uppercase font-bold">
                          <AlertCircle size={14} strokeWidth={1.5} /> Reorder
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 font-data text-[10px] tracking-[0.15em] uppercase text-muted-foreground">
                          <CheckCircle size={14} strokeWidth={1.5} /> Healthy
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <button className={`font-data text-[10px] tracking-[0.2em] uppercase border-b border-current hover:border-b-2 transition-all duration-100 focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-3 ${
                        isCritical ? 'focus-visible:outline-background' : 'focus-visible:outline-foreground'
                      }`}>
                        Order
                      </button>
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
