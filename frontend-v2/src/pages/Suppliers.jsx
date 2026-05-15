import { useEffect, useState } from 'react';
import { fetchSuppliers } from '../api';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetchSuppliers();
        setSuppliers(res.data);
      } catch (err) {
        console.error("Failed to load suppliers", err);
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

  return (
    <div className="space-y-8">
      <div>
        <p className="font-data text-[11px] tracking-[0.3em] uppercase text-muted-foreground mb-3">
          Vendor Network
        </p>
        <h1 className="font-display text-6xl font-bold tracking-tight leading-none">
          Suppliers
        </h1>
        <hr className="section-rule mt-6" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-0 border-2 border-foreground">
        {suppliers.map((sup, idx) => (
          <div
            key={sup.supplier_id}
            className={`group p-6 flex flex-col transition-colors duration-100 hover:bg-foreground hover:text-background ${
              /* Right border for all except last in row */
              (idx + 1) % 3 !== 0 ? 'border-r border-foreground' : ''
            } ${
              /* Bottom border for all except last row */
              idx < suppliers.length - 3 ? 'border-b border-foreground' : ''
            }`}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-display text-xl font-bold tracking-tight">{sup.name}</h3>
                <p className="font-data text-[10px] tracking-[0.15em] uppercase text-muted-foreground group-hover:text-background/60 mt-1">
                  {sup.city}, {sup.state}
                </p>
              </div>
              {sup.is_emergency_certified && (
                <span className="font-data text-[9px] tracking-[0.2em] uppercase font-bold px-2 py-1 border border-current whitespace-nowrap">
                  Emergency
                </span>
              )}
            </div>

            <div className="space-y-4 mt-auto">
              {/* Reliability */}
              <div>
                <div className="flex justify-between font-data text-[10px] tracking-[0.15em] uppercase mb-2">
                  <span className="text-muted-foreground group-hover:text-background/60">Reliability</span>
                  <span className="font-bold">{Math.round(sup.reliability_score * 100)}%</span>
                </div>
                <div className="w-full h-0.5 bg-border-light group-hover:bg-background/20">
                  <div
                    className="h-0.5 bg-foreground group-hover:bg-background transition-colors duration-100"
                    style={{width: `${sup.reliability_score * 100}%`}}
                  />
                </div>
              </div>

              {/* Lead Time */}
              <div className="flex justify-between items-center font-data text-[10px] tracking-[0.15em] uppercase border-t border-border-light group-hover:border-background/20 pt-3">
                <span className="text-muted-foreground group-hover:text-background/60">Lead Time</span>
                <span className="font-display text-lg font-bold">{sup.avg_lead_days}d</span>
              </div>

              {/* Categories */}
              <div className="flex justify-between items-start border-t border-border-light group-hover:border-background/20 pt-3">
                <span className="font-data text-[10px] tracking-[0.15em] uppercase text-muted-foreground group-hover:text-background/60">Categories</span>
                <div className="flex flex-wrap gap-1 justify-end max-w-[60%]">
                  {sup.supply_categories.map(cat => (
                    <span key={cat} className="font-data text-[9px] tracking-[0.1em] uppercase px-2 py-0.5 border border-current">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
