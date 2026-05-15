import { useEffect, useState } from 'react';
import { fetchSuppliers } from '../api';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try { const res = await fetchSuppliers(); setSuppliers(res.data); }
      catch (e) { console.error(e); }
      finally { setLoading(false); }
    })();
  }, []);

  if (loading) return <div className="flex h-64 items-center justify-center"><div className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6 max-w-[1200px]">
      <div>
        <p className="text-[11px] font-mono tracking-widest uppercase text-fg-muted mb-2">Vendor Network</p>
        <h1 className="text-5xl font-semibold tracking-tight bg-gradient-to-b from-white via-white/95 to-white/70 bg-clip-text text-transparent">Suppliers</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {suppliers.map(sup => (
          <div key={sup.supplier_id} className="group p-5 rounded-2xl border border-border bg-gradient-to-b from-white/[0.06] to-white/[0.02] hover:border-border-hover hover:shadow-[0_8px_40px_rgba(0,0,0,0.4),0_0_60px_rgba(94,106,210,0.06)] transition-all duration-300 flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-base font-semibold text-fg tracking-tight">{sup.name}</h3>
                <p className="text-xs text-fg-muted mt-0.5">{sup.city}, {sup.state}</p>
              </div>
              {sup.is_emergency_certified && (
                <span className="text-[9px] font-semibold tracking-wider uppercase px-2 py-1 rounded-full bg-danger/15 text-danger border border-danger/20">Emergency</span>
              )}
            </div>

            <div className="space-y-4 mt-auto">
              {/* Reliability */}
              <div>
                <div className="flex justify-between text-[10px] font-mono tracking-widest uppercase text-fg-muted mb-1.5">
                  <span>Reliability</span>
                  <span className="font-semibold text-fg">{Math.round(sup.reliability_score * 100)}%</span>
                </div>
                <div className="w-full h-1 rounded-full bg-white/10">
                  <div
                    className={`h-1 rounded-full transition-all duration-500 ${
                      sup.reliability_score >= 0.8 ? 'bg-success shadow-[0_0_8px_rgba(48,164,108,0.4)]' :
                      sup.reliability_score >= 0.6 ? 'bg-warning shadow-[0_0_8px_rgba(245,166,35,0.4)]' :
                      'bg-danger shadow-[0_0_8px_rgba(229,72,77,0.4)]'
                    }`}
                    style={{width: `${sup.reliability_score * 100}%`}}
                  />
                </div>
              </div>

              {/* Lead Time */}
              <div className="flex justify-between items-center text-sm border-t border-border pt-3">
                <span className="text-[10px] font-mono tracking-widest uppercase text-fg-muted">Lead Time</span>
                <span className="font-semibold text-fg">{sup.avg_lead_days}d</span>
              </div>

              {/* Categories */}
              <div className="flex flex-wrap gap-1.5 border-t border-border pt-3">
                {sup.supply_categories.map(cat => (
                  <span key={cat} className="text-[10px] font-mono tracking-wider px-2 py-0.5 rounded-full bg-white/[0.05] text-fg-muted border border-border">{cat}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
