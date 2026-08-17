import { X, MapPin, AlertTriangle, TreePine, Home, CheckCircle2 } from 'lucide-react';
import { useHotspotDetail } from '../../api/queries';
import type { OptimizeResponse } from '../../data/types';

interface FeaturePanelProps {
  activeCityId: string;
  featureId: string;
  onClose: () => void;
  optimizationData?: { cityId: string; data: OptimizeResponse } | null;
}

export default function FeaturePanel({ activeCityId, featureId, onClose, optimizationData }: FeaturePanelProps) {
  const { data, isLoading, isError } = useHotspotDetail(activeCityId, featureId);

  if (isLoading) {
    return (
      <div className="w-80 sm:w-96 bg-zinc-900 border border-zinc-700 shadow-xl rounded-lg overflow-hidden flex flex-col h-64 p-6 items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-400 mb-4"></div>
        <p className="text-sm text-zinc-400">Loading hotspot details...</p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="w-80 sm:w-96 bg-zinc-900 border border-zinc-700 shadow-xl rounded-lg overflow-hidden flex flex-col">
        <div className="p-4 border-b border-zinc-800 bg-zinc-950 flex items-start justify-between">
          <h2 className="text-lg font-medium text-white">Error</h2>
          <button onClick={onClose} className="p-1 hover:bg-zinc-800 rounded-md text-zinc-400">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-3" />
          <p className="text-sm text-zinc-400">Failed to load details for this feature.</p>
        </div>
      </div>
    );
  }

  const p1 = data.feature.properties;
  
  const p3Allocations = optimizationData?.cityId === activeCityId 
    ? optimizationData.data.hotspot_allocations.filter(a => a.hotspot_id === featureId)
    : [];

  return (
    <div className="w-80 sm:w-96 bg-zinc-900 border border-zinc-700 shadow-xl rounded-lg overflow-hidden flex flex-col max-h-[calc(100vh-2rem)]">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 bg-zinc-950 flex items-start justify-between">
        <div>
          <h2 className="text-lg font-medium text-white flex items-center gap-2">
            <MapPin className="w-4 h-4 text-zinc-400" />
            Spatial Feature
          </h2>
          <p className="text-xs text-zinc-400 mt-1 uppercase tracking-wider">{data.feature.id}</p>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-zinc-800 rounded-md text-zinc-400 transition-colors">
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4 overflow-y-auto space-y-6">

        {/* P3 Data: Mitigation Recommendations */}
        {p3Allocations.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-emerald-500 uppercase tracking-wider mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              P3 Recommended Intervention
            </h3>
            <div className="space-y-3">
              {p3Allocations.map(alloc => (
                <div key={alloc.intervention} className="bg-emerald-950/20 border border-emerald-900/50 p-4 rounded-md">
                  <div className="flex items-center gap-2 mb-3">
                    {alloc.intervention === 'tree_canopy' ? (
                      <TreePine className="text-emerald-500 w-5 h-5" />
                    ) : (
                      <Home className="text-sky-500 w-5 h-5" />
                    )}
                    <span className="font-semibold text-white">
                      {alloc.intervention === 'tree_canopy' ? 'Tree Canopy' : 'Cool Roof'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="block text-xs text-zinc-500 mb-0.5">Intensity</span>
                      <span className="text-zinc-200 font-medium">{alloc.intensity_allocated.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="block text-xs text-zinc-500 mb-0.5">Cost Est.</span>
                      <span className="text-zinc-200 font-medium">{alloc.resource_units_used.toFixed(0)}</span>
                    </div>
                    <div className="col-span-2 mt-1">
                      <span className="block text-xs text-zinc-500 mb-0.5">Expected Cooling</span>
                      <span className="text-blue-400 font-medium text-lg">-{alloc.expected_cooling_celsius.toFixed(2)} °C</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* P1 Data: Core Observation */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">LST Observation</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800">
              <span className="block text-xs text-zinc-400 mb-1">LST (°C)</span>
              <span className="text-xl font-semibold text-white">{p1.lst_c?.toFixed(1) ?? '--'}°</span>
            </div>
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800 flex flex-col justify-center">
              <span className="block text-xs text-zinc-400 mb-1">Anomaly Baseline</span>
              {p1.lst_anomaly_c != null ? (
                <span className={`text-xl font-semibold ${p1.lst_anomaly_c > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                  {p1.lst_anomaly_c > 0 ? '+' : ''}{p1.lst_anomaly_c.toFixed(1)}°
                </span>
              ) : (
                <span className="text-sm text-zinc-500 italic">N/A</span>
              )}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800">
              <span className="block text-xs text-zinc-400 mb-1">NDVI (Veg)</span>
              <span className="text-sm font-semibold text-white">{p1.ndvi_mean?.toFixed(3) ?? '--'}</span>
            </div>
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800">
              <span className="block text-xs text-zinc-400 mb-1">NDBI (Built)</span>
              <span className="text-sm font-semibold text-white">{p1.ndbi_mean?.toFixed(3) ?? '--'}</span>
            </div>
            <div className="bg-zinc-950 p-3 rounded-md border border-zinc-800">
              <span className="block text-xs text-zinc-400 mb-1">NDWI (Water)</span>
              <span className="text-sm font-semibold text-white">{p1.ndwi_mean?.toFixed(3) ?? '--'}</span>
            </div>
          </div>
        </section>

        {/* P2 Data: Risk & Vulnerability */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">Vulnerability & Risk</h3>
          {data.risk ? (
            data.risk.hotspot_id ? (
              <div className="space-y-4">
                <div className="bg-zinc-950 p-4 rounded-md border border-zinc-800">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className={`w-4 h-4 ${data.risk.p2_analysis.risk_category === 'high' || data.risk.p2_analysis.risk_category === 'severe' ? 'text-red-500' : 'text-orange-500'}`} />
                    <span className="font-medium text-white capitalize">{data.risk.p2_analysis.risk_category} Risk</span>
                  </div>
                  <div className="text-3xl font-bold text-white mb-1">{data.risk.p2_analysis.risk_score.toFixed(2)}<span className="text-lg text-zinc-500 font-normal">/100</span></div>
                  <div className="text-xs text-zinc-400">Integrated heat vulnerability & risk score</div>
                </div>

                {data.risk.p2_analysis.contributors && data.risk.p2_analysis.contributors.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-zinc-300 mb-2">Key Drivers</h4>
                    <div className="space-y-2">
                      {data.risk.p2_analysis.contributors.map((driver, idx) => (
                        <div key={idx} className="bg-zinc-950 p-2 rounded border border-zinc-800">
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-zinc-400 capitalize">{driver.name}</span>
                            <span className="text-zinc-300">{driver.value.toFixed(2)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-blue-500 rounded-full"
                                style={{ width: `${driver.importance * 100}%` }}
                              />
                            </div>
                            <span className="text-zinc-300 w-8 text-right">{(driver.importance * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-between items-center text-sm">
                  <span className="text-zinc-400">Hotspot ID</span>
                  <span className="text-zinc-300 font-medium font-mono text-[10px]">{data.risk.hotspot_id}</span>
                </div>
              </div>
            ) : (
              <div className="bg-zinc-900/50 p-4 rounded-md border border-zinc-800 text-center">
                <span className="text-sm text-zinc-400 block mb-1">No canonical P2 hotspot classification</span>
                <span className="text-xs text-zinc-500">This feature does not meet the backend risk thresholds for hotspot designation.</span>
              </div>
            )
          ) : (
            <div className="bg-zinc-950 border border-zinc-800 border-dashed rounded-md p-4 text-center">
              <p className="text-sm text-zinc-500">Risk model data not yet available for this feature.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
