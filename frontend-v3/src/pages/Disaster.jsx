import { useEffect, useMemo, useRef, useState } from 'react';
import { DeckGL } from '@deck.gl/react';
import { GeoJsonLayer, PathLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import { circle as turfCircle } from '@turf/turf';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { AlertTriangle, CheckCircle2, MapPinned, PlayCircle, Radio, RefreshCw, Route } from 'lucide-react';
import { format } from 'date-fns';
import { fetchDisasterEvents, fetchDisasterMapData, simulateDisaster, triggerDisasterCheck } from '../api';

const MAP_STYLE = {
  version: 8,
  sources: {
    cartoDark: {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'https://d.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    },
  },
  layers: [
    {
      id: 'carto-dark',
      type: 'raster',
      source: 'cartoDark',
      minzoom: 0,
      maxzoom: 20,
      paint: {
        'raster-opacity': 1,
        'raster-brightness-min': 0.08,
        'raster-brightness-max': 0.9,
        'raster-saturation': -0.15,
        'raster-contrast': 0.32,
      },
    },
  ],
};

const INITIAL_VIEW_STATE = {
  longitude: 77.5946,
  latitude: 12.9716,
  zoom: 6.2,
  pitch: 42,
  bearing: -8,
};

function extractPaths(geojson) {
  if (!geojson) return [];

  const geometries = geojson.type === 'FeatureCollection'
    ? geojson.features.map((feature) => feature.geometry)
    : [geojson.type === 'Feature' ? geojson.geometry : geojson];

  return geometries.flatMap((geometry) => {
    if (!geometry) return [];
    if (geometry.type === 'LineString') return [geometry.coordinates];
    if (geometry.type === 'MultiLineString') return geometry.coordinates;
    return [];
  });
}

function buildDashedSegments(path) {
  const segments = [];
  const steps = 16;

  for (let index = 0; index < path.length - 1; index += 1) {
    const start = path[index];
    const end = path[index + 1];

    for (let step = 0; step < steps; step += 2) {
      const from = step / steps;
      const to = Math.min((step + 1) / steps, 1);
      segments.push([
        [
          start[0] + (end[0] - start[0]) * from,
          start[1] + (end[1] - start[1]) * from,
        ],
        [
          start[0] + (end[0] - start[0]) * to,
          start[1] + (end[1] - start[1]) * to,
        ],
      ]);
    }
  }

  return segments;
}

function formatEta(hours) {
  if (!hours && hours !== 0) return 'Calculating';
  if (hours >= 24) return `${Math.round(hours / 24)}d`;
  return `${Number(hours).toFixed(1)}h`;
}

function supplierColor(supplier) {
  if (supplier.inside_disaster_zone || supplier.risk_level === 'blocked') return [248, 81, 73, 235];
  if (supplier.is_govt_reserve) return [250, 204, 21, 235];
  if (supplier.emergency_certified) return [168, 85, 247, 235];
  if (supplier.risk_level === 'medium') return [251, 191, 36, 225];
  return [34, 197, 94, 225];
}

function StatPill({ label, value, tone = 'slate' }) {
  const tones = {
    cyan: 'border-[#5E6AD2]/30 bg-[#5E6AD2]/10 text-[#EDEDEF]',
    red: 'border-red-400/20 bg-red-500/8 text-[#EDEDEF]',
    green: 'border-emerald-400/20 bg-emerald-500/8 text-[#EDEDEF]',
    slate: 'border-white/[0.06] bg-white/[0.04] text-[#EDEDEF]',
  };

  return (
    <div className={`rounded-2xl border px-4 py-3 ${tones[tone]}`}>
      <p className="text-[10px] font-mono uppercase tracking-widest opacity-60">{label}</p>
      <p className="mt-1 text-lg font-semibold tracking-tight">{value}</p>
    </div>
  );
}

export default function Disaster() {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const [activeEvent, setActiveEvent] = useState(null);
  const [history, setHistory] = useState([]);
  const [hospital, setHospital] = useState({
    lat: 12.9716,
    lng: 77.5946,
    city: 'Bengaluru',
    name: 'Bengaluru Central Hospital',
  });
  const [suppliers, setSuppliers] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [demandSurge, setDemandSurge] = useState([]);
  const [emergencySuppliers, setEmergencySuppliers] = useState([]);
  const [selectedRouteId, setSelectedRouteId] = useState(null);
  const [activeTab, setActiveTab] = useState('orders');
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const loadData = async () => {
    try {
      const [mapRes, histRes] = await Promise.all([
        fetchDisasterMapData(),
        fetchDisasterEvents(),
      ]);

      const data = mapRes.data;
      setHospital(data.hospital);
      setActiveEvent(data.event);
      setSuppliers(data.suppliers || []);
      setRoutes(data.routes || []);
      setDemandSurge(data.demand_surge || []);
      setEmergencySuppliers(data.emergency_suppliers || []);
      setHistory(histRes.data);
      setSelectedRouteId((current) => (
        data.routes?.some((route) => route.route_id === current)
          ? current
          : data.routes?.[0]?.route_id || null
      ));

      const center = data.event || data.hospital;
      setViewState((current) => ({
        ...current,
        longitude: center.lng,
        latitude: center.lat,
        zoom: data.event ? 6.4 : 6.1,
      }));
    } catch (err) {
      console.error('Failed to load disaster info', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadInitialData = async () => {
      await loadData();
    };

    void loadInitialData();
  }, []);

  useEffect(() => {
    if (loading || !mapContainerRef.current || mapRef.current) return;

    mapRef.current = new maplibregl.Map({
      container: mapContainerRef.current,
      style: MAP_STYLE,
      center: [INITIAL_VIEW_STATE.longitude, INITIAL_VIEW_STATE.latitude],
      zoom: INITIAL_VIEW_STATE.zoom,
      pitch: INITIAL_VIEW_STATE.pitch,
      bearing: INITIAL_VIEW_STATE.bearing,
      interactive: false,
      attributionControl: false,
    });

    mapRef.current.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right');
    mapRef.current.once('load', () => mapRef.current?.resize());

    const observer = new ResizeObserver(() => {
      mapRef.current?.resize();
    });
    observer.observe(mapContainerRef.current);

    return () => {
      observer.disconnect();
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [loading]);

  useEffect(() => {
    if (!mapRef.current) return;

    mapRef.current.jumpTo({
      center: [viewState.longitude, viewState.latitude],
      zoom: viewState.zoom,
      pitch: viewState.pitch,
      bearing: viewState.bearing,
    });
  }, [viewState]);

  const selectedRoute = routes.find((route) => route.route_id === selectedRouteId) || routes[0];
  const disasterZone = useMemo(() => {
    if (!activeEvent?.lat || !activeEvent?.lng) return null;
    return activeEvent.zone_geojson || turfCircle(
      [activeEvent.lng, activeEvent.lat],
      activeEvent.affected_radius_km || 150,
      { steps: 64, units: 'kilometers' },
    );
  }, [activeEvent]);

  const warningZone = useMemo(() => {
    if (!activeEvent?.lat || !activeEvent?.lng) return null;
    return turfCircle(
      [activeEvent.lng, activeEvent.lat],
      (activeEvent.affected_radius_km || 150) * 1.18,
      { steps: 64, units: 'kilometers' },
    );
  }, [activeEvent]);

  const routeLayerData = useMemo(() => {
    const original = routes.flatMap((route) => (
      extractPaths(route.original_route_geojson).flatMap((path) => (
        buildDashedSegments(path).map((segment) => ({ ...route, path: segment }))
      ))
    ));
    const alternate = routes.flatMap((route) => (
      extractPaths(route.alternate_route_geojson).map((path) => ({ ...route, path }))
    ));

    return { original, alternate };
  }, [routes]);

  const movementDots = useMemo(() => (
    routeLayerData.alternate.flatMap((route) => route.path
      .filter((_, index) => index > 0 && index % Math.max(1, Math.floor(route.path.length / 5)) === 0)
      .map((position) => ({ ...route, position })))
  ), [routeLayerData.alternate]);

  const layers = [
    warningZone && new GeoJsonLayer({
      id: 'warning-zone',
      data: warningZone,
      stroked: true,
      filled: false,
      getLineColor: [251, 146, 60, 210],
      getLineWidth: 4200,
      lineWidthMinPixels: 2,
    }),
    disasterZone && new GeoJsonLayer({
      id: 'disaster-zone',
      data: disasterZone,
      stroked: true,
      filled: true,
      getFillColor: activeEvent?.severity >= 4 ? [239, 68, 68, 80] : [251, 146, 60, 70],
      getLineColor: [248, 113, 113, 240],
      getLineWidth: 5000,
      lineWidthMinPixels: 3,
    }),
    new PathLayer({
      id: 'original-routes',
      data: routeLayerData.original,
      getPath: (route) => route.path,
      getColor: [248, 81, 73, 235],
      getWidth: 2600,
      widthMinPixels: 3,
      pickable: true,
    }),
    new PathLayer({
      id: 'alternate-routes-glow',
      data: routeLayerData.alternate,
      getPath: (route) => route.path,
      getColor: [34, 211, 238, 65],
      getWidth: 9800,
      widthMinPixels: 8,
    }),
    new PathLayer({
      id: 'alternate-routes',
      data: routeLayerData.alternate,
      getPath: (route) => route.path,
      getColor: (route) => route.route_id === selectedRoute?.route_id ? [52, 211, 153, 245] : [34, 211, 238, 220],
      getWidth: (route) => route.route_id === selectedRoute?.route_id ? 5200 : 3800,
      widthMinPixels: 5,
      pickable: true,
    }),
    new ScatterplotLayer({
      id: 'route-motion-dots',
      data: movementDots,
      getPosition: (dot) => dot.position,
      getRadius: 9000,
      radiusMinPixels: 4,
      radiusMaxPixels: 9,
      getFillColor: [190, 242, 100, 220],
    }),
    new ScatterplotLayer({
      id: 'hospital-marker',
      data: [{ ...hospital, type: 'hospital' }],
      getPosition: (point) => [point.lng, point.lat],
      getRadius: 18000,
      radiusMinPixels: 13,
      radiusMaxPixels: 24,
      getFillColor: [59, 130, 246, 245],
      getLineColor: [219, 234, 254, 255],
      lineWidthMinPixels: 3,
      stroked: true,
      pickable: true,
    }),
    new ScatterplotLayer({
      id: 'supplier-markers',
      data: suppliers,
      getPosition: (supplier) => [supplier.lng, supplier.lat],
      getRadius: (supplier) => supplier.supplier_id === selectedRoute?.supplier_id ? 15000 : 11000,
      radiusMinPixels: (supplier) => supplier.supplier_id === selectedRoute?.supplier_id ? 11 : 7,
      radiusMaxPixels: 18,
      getFillColor: supplierColor,
      getLineColor: [255, 255, 255, 230],
      lineWidthMinPixels: 2,
      stroked: true,
      pickable: true,
    }),
    new TextLayer({
      id: 'map-labels',
      data: [
        activeEvent && {
          label: `${activeEvent.disaster_type?.toUpperCase()} ZONE`,
          lng: activeEvent.lng,
          lat: activeEvent.lat,
          color: [254, 202, 202, 255],
        },
        {
          label: hospital.city,
          lng: hospital.lng,
          lat: hospital.lat,
          color: [191, 219, 254, 255],
        },
        ...routes.slice(0, 4).map((route) => ({
          label: route.supplier_name || 'Supplier',
          lng: route.supplier_lng,
          lat: route.supplier_lat,
          color: [220, 252, 231, 255],
        })),
      ].filter(Boolean),
      getPosition: (label) => [label.lng, label.lat],
      getText: (label) => label.label,
      getColor: (label) => label.color,
      getSize: 13,
      getPixelOffset: [0, -22],
      fontWeight: 700,
    }),
  ].filter(Boolean);

  const handleManualTrigger = async () => {
    setChecking(true);
    try {
      await triggerDisasterCheck();
      window.dispatchEvent(new Event('disaster:changed'));
      await loadData();
    } catch (err) {
      console.error('Manual trigger failed', err);
    } finally {
      setChecking(false);
    }
  };

  const handleSimulate = async () => {
    setChecking(true);
    try {
      await simulateDisaster();
      window.dispatchEvent(new Event('disaster:changed'));
      await loadData();
    } catch (err) {
      console.error('Simulate failed', err);
    } finally {
      setChecking(false);
    }
  };

  if (loading) return <div className="flex h-64 items-center justify-center"><div className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" /></div>;

  return (
    <div className="-m-8 min-h-screen bg-[#050506] bg-[radial-gradient(ellipse_at_top,#0a0a0f_0%,#050506_50%,#020203_100%),linear-gradient(rgba(148,163,184,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.04)_1px,transparent_1px)] bg-[length:auto,64px_64px,64px_64px] p-6 text-[#EDEDEF]">
      <div className="mb-5 flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 shadow-2xl backdrop-blur lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-[10px] font-mono uppercase tracking-widest text-[#8A8F98]">Emergency logistics command center</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight bg-gradient-to-b from-white to-white/70 bg-clip-text text-transparent">
            {activeEvent ? 'Disaster Mode Active' : 'Disaster Intelligence'}
          </h1>
          <p className="mt-1 max-w-4xl text-sm text-slate-300">
            {activeEvent
              ? `${activeEvent.raw_text} Radius ${activeEvent.affected_radius_km || 150} km near ${activeEvent.location_name}.`
              : 'No active incident is declared. The control tower is ready to model affected supplier routes.'}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleSimulate}
            disabled={checking}
            className="flex items-center gap-2 rounded-lg bg-red-500 px-4 py-2.5 text-sm font-semibold text-white shadow-[0_0_0_1px_rgba(229,72,77,0.5),0_4px_12px_rgba(229,72,77,0.3)] transition-all duration-200 hover:bg-red-400 hover:shadow-[0_0_0_1px_rgba(229,72,77,0.6),0_8px_20px_rgba(229,72,77,0.4)] active:scale-[0.98] disabled:opacity-50"
          >
            <PlayCircle size={16} />
            Simulate Disaster
          </button>
          <button
            onClick={handleManualTrigger}
            disabled={checking}
            className="flex items-center gap-2 rounded-lg bg-[#5E6AD2] px-4 py-2.5 text-sm font-semibold text-white shadow-[0_0_0_1px_rgba(94,106,210,0.5),0_4px_12px_rgba(94,106,210,0.3),inset_0_1px_0_0_rgba(255,255,255,0.15)] transition-all duration-200 hover:bg-[#6872D9] hover:shadow-[0_0_0_1px_rgba(94,106,210,0.6),0_8px_20px_rgba(94,106,210,0.4)] active:scale-[0.98] disabled:opacity-50"
          >
            <RefreshCw size={16} className={checking ? 'animate-spin' : ''} />
            {checking ? 'Scanning...' : 'Force Live Scan'}
          </button>
        </div>
      </div>

      <div className="mb-5 grid grid-cols-1 gap-4 lg:grid-cols-4">
        <StatPill label="Incident Status" value={activeEvent ? `Severity ${activeEvent.severity}/5` : 'All Clear'} tone={activeEvent ? 'red' : 'green'} />
        <StatPill label="Affected Orders" value={routes.length} tone="cyan" />
        <StatPill label="Emergency Suppliers" value={emergencySuppliers.length} tone="green" />
        <StatPill label="Demand Surge Items" value={demandSurge.length} />
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <section className="relative h-[620px] overflow-hidden rounded-3xl border border-white/10 bg-slate-950 shadow-2xl">
          <div className="absolute inset-0">
            <div ref={mapContainerRef} className="h-full w-full" />
          </div>
          <DeckGL
            width="100%"
            height="100%"
            style={{ position: 'absolute', inset: 0, zIndex: 1 }}
            viewState={viewState}
            controller
            layers={layers}
            onViewStateChange={({ viewState: nextViewState }) => setViewState(nextViewState)}
            getTooltip={({ object }) => {
              if (!object) return null;
              if (object.type === 'hospital') return `${hospital.name}\nReceiving hub`;
              if (object.supplier_id) return `${object.name || object.supplier_name}\nRisk: ${object.risk_level || object.disruption_risk || 'route'}\nETA: ${formatEta(object.alternate_eta_hours)}`;
              return null;
            }}
          />

          <div className="absolute bottom-5 left-5 rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-xs shadow-xl backdrop-blur">
            <p className="mb-3 font-bold uppercase tracking-[0.2em] text-slate-300">Map Legend</p>
            {[
              ['bg-blue-500', 'Hospital'],
              ['bg-emerald-400', 'Safe supplier'],
              ['bg-amber-400', 'At-risk / reserve'],
              ['bg-red-500', 'Blocked supplier'],
              ['bg-purple-500', 'Emergency certified'],
              ['border-t-2 border-dashed border-red-400', 'Original blocked route'],
              ['border-t-4 border-cyan-300', 'Recommended alternate route'],
            ].map(([style, label]) => (
              <div key={label} className="mb-2 flex items-center gap-2 text-slate-200 last:mb-0">
                <span className={`inline-block h-3 w-7 rounded-full ${style}`} />
                {label}
              </div>
            ))}
          </div>

          {activeEvent && (
            <div className="absolute right-5 top-5 max-w-sm rounded-2xl border border-red-300/20 bg-red-950/70 p-4 shadow-xl backdrop-blur">
              <p className="flex items-center gap-2 text-sm font-bold text-red-100">
                <AlertTriangle size={17} />
                {activeEvent.disaster_type?.toUpperCase()} ZONE
              </p>
              <p className="mt-2 text-xs leading-5 text-red-100/80">
                Red polygon marks the affected area. Cyan/green corridors are alternate routes requested with disaster avoidance geometry.
              </p>
            </div>
          )}
        </section>

        <aside className="space-y-5">
          <section className="rounded-3xl border border-white/10 bg-white/7 p-5 shadow-2xl backdrop-blur">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-black">
                <Route className="text-cyan-300" />
                Route Decision
              </h2>
              {selectedRoute && <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-bold text-emerald-200">Recommended</span>}
            </div>

            {selectedRoute ? (
              <div className="space-y-4">
                <select
                  value={selectedRoute.route_id}
                  onChange={(event) => setSelectedRouteId(event.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none"
                >
                  {routes.map((route) => (
                    <option key={route.route_id} value={route.route_id}>
                      {route.order_id || 'Route'} - {route.supplier_name || 'Supplier'}
                    </option>
                  ))}
                </select>

                <div className="rounded-2xl border border-cyan-300/20 bg-cyan-400/10 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Recommended Route</p>
                  <p className="mt-1 text-xl font-black">{selectedRoute.supplier_name} to {hospital.city}</p>
                  <p className="mt-2 text-sm text-slate-300">{selectedRoute.item_name || 'Emergency medical supplies'} {selectedRoute.quantity ? `x ${selectedRoute.quantity}` : ''}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <StatPill label="Original" value={selectedRoute.original_status?.toUpperCase() || 'BLOCKED'} tone="red" />
                  <StatPill label="Alternate ETA" value={formatEta(selectedRoute.alternate_eta_hours)} tone="green" />
                  <StatPill label="Distance" value={selectedRoute.alternate_distance_km ? `${selectedRoute.alternate_distance_km} km` : 'Road path'} />
                  <StatPill label="Risk Reduced" value={`${selectedRoute.risk_reduction_percent || 82}%`} tone="cyan" />
                </div>

                <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                  <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Why this route?</p>
                  <p className="text-sm leading-6 text-slate-200">{selectedRoute.reason}</p>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs">
                    <span className="rounded-full bg-white/10 px-3 py-1">Supplier reliability {Math.round((selectedRoute.supplier_reliability_score || 0) * 100)}%</span>
                    <span className="rounded-full bg-white/10 px-3 py-1">{selectedRoute.supplier_emergency_certified ? 'Emergency certified' : 'Standard supplier'}</span>
                    <span className="rounded-full bg-white/10 px-3 py-1">Mode {selectedRoute.alternate_mode || 'road'}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-300">No affected routes are currently marked. Trigger a simulation to generate a response plan.</p>
            )}
          </section>

          <section className={`rounded-3xl border p-5 shadow-2xl backdrop-blur ${activeEvent ? 'border-red-300/20 bg-red-950/35' : 'border-emerald-300/20 bg-emerald-950/25'}`}>
            <h2 className="mb-3 flex items-center gap-2 text-lg font-black">
              {activeEvent ? <AlertTriangle className="text-red-300" /> : <Radio className="text-emerald-300" />}
              {activeEvent ? 'Active Incident' : 'All Clear'}
            </h2>
            {activeEvent ? (
              <div className="space-y-3 text-sm text-slate-200">
                <p className="font-bold text-red-100">{activeEvent.location_name}</p>
                <p>{activeEvent.summary || 'Analyzing live risk signal...'}</p>
                <p className="text-xs text-slate-300">Detected {format(new Date(activeEvent.detected_at), 'MMM dd HH:mm')} from {activeEvent.source}</p>
              </div>
            ) : (
              <p className="text-sm text-slate-300">No active disasters detected near supply routes.</p>
            )}
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/7 p-5 shadow-2xl backdrop-blur">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-black">
              <MapPinned className="text-amber-300" />
              Recent Events
            </h2>
            <div className="max-h-[180px] space-y-3 overflow-y-auto pr-1">
              {history.filter((event) => !event.is_active).slice(0, 5).map((event) => (
                <div key={event.event_id} className="rounded-xl bg-white/5 p-3 text-sm">
                  <p className="truncate font-semibold text-slate-100" title={event.raw_text}>{event.raw_text}</p>
                  <div className="mt-1 flex justify-between text-xs text-slate-400">
                    <span className="capitalize">{event.source}</span>
                    <span>{format(new Date(event.detected_at), 'MMM dd')}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>

      <section className="mt-5 rounded-3xl border border-white/10 bg-white/7 p-5 shadow-2xl backdrop-blur">
        <div className="mb-4 flex flex-wrap gap-3">
          {[
            ['orders', 'Affected Orders'],
            ['suppliers', 'Emergency Suppliers'],
            ['surge', 'Demand Surge'],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`rounded-xl px-4 py-2 text-sm font-bold transition ${activeTab === key ? 'bg-cyan-300 text-slate-950' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}
            >
              {label}
            </button>
          ))}
        </div>

        {activeTab === 'orders' && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.18em] text-slate-400">
                <tr>
                  <th className="px-3 py-2">Order ID</th>
                  <th className="px-3 py-2">Item</th>
                  <th className="px-3 py-2">Supplier</th>
                  <th className="px-3 py-2">Route Risk</th>
                  <th className="px-3 py-2">Original ETA</th>
                  <th className="px-3 py-2">Alternate ETA</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {routes.map((route) => (
                  <tr key={route.route_id} className="border-t border-white/10">
                    <td className="px-3 py-3 font-mono text-xs">{route.order_id}</td>
                    <td className="px-3 py-3">{route.item_name || 'Medical supplies'}</td>
                    <td className="px-3 py-3">{route.supplier_name}</td>
                    <td className="px-3 py-3 text-red-200">{route.disruption_risk || 'high'}</td>
                    <td className="px-3 py-3">{formatEta(route.original_eta_hours)}</td>
                    <td className="px-3 py-3 text-emerald-200">{formatEta(route.alternate_eta_hours)}</td>
                    <td className="px-3 py-3"><span className="rounded-full bg-cyan-300/15 px-3 py-1 text-xs font-bold text-cyan-200">Rerouted</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!routes.length && <p className="py-6 text-sm text-slate-300">No affected orders yet.</p>}
          </div>
        )}

        {activeTab === 'suppliers' && (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {emergencySuppliers.map((supplier, index) => (
              <div key={supplier.supplier_id} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                <div className="flex items-center justify-between">
                  <p className="font-bold">{index + 1}. {supplier.name}</p>
                  {supplier.emergency_certified && <CheckCircle2 className="text-emerald-300" size={18} />}
                </div>
                <p className="mt-1 text-sm text-slate-300">{supplier.city}, {supplier.state}</p>
                <div className="mt-3 flex gap-2 text-xs">
                  <span className="rounded-full bg-white/10 px-3 py-1">{Math.round(supplier.reliability_score * 100)}% reliable</span>
                  <span className="rounded-full bg-white/10 px-3 py-1">{supplier.avg_lead_days}d lead</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'surge' && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.18em] text-slate-400">
                <tr>
                  <th className="px-3 py-2">Item</th>
                  <th className="px-3 py-2">Current Stock</th>
                  <th className="px-3 py-2">Surge Multiplier</th>
                  <th className="px-3 py-2">Stockout Hours</th>
                  <th className="px-3 py-2">Recommended Qty</th>
                  <th className="px-3 py-2">Urgency</th>
                </tr>
              </thead>
              <tbody>
                {demandSurge.map((surge) => (
                  <tr key={surge.item_id} className="border-t border-white/10">
                    <td className="px-3 py-3">{surge.item_name}</td>
                    <td className="px-3 py-3">{surge.current_stock ?? 'N/A'}</td>
                    <td className="px-3 py-3">{surge.surge_multiplier}x</td>
                    <td className="px-3 py-3">{surge.stockout_hours ? `${Math.round(surge.stockout_hours)}h` : 'N/A'}</td>
                    <td className="px-3 py-3">{surge.recommended_order_qty}</td>
                    <td className="px-3 py-3 text-amber-200">{surge.urgency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!demandSurge.length && <p className="py-6 text-sm text-slate-300">No surge predictions for the active incident yet.</p>}
          </div>
        )}
      </section>
    </div>
  );
}
