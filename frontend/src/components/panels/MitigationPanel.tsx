import { useState, useMemo } from 'react';
import { useCityMap } from '../../api/queries';
import { useOptimizationMutation } from '../../api/mutations';
import { ThermometerSun, AlertCircle, CheckCircle2, ServerCrash, TreePine, Home } from 'lucide-react';
import type { OptimizeResponse } from '../../data/types';

interface MitigationPanelProps {
  activeCityId: string | null;
  optimizationData: { cityId: string; data: OptimizeResponse } | null;
  onOptimizationSuccess: (data: OptimizeResponse) => void;
}

const INTERVENTIONS = [
  {
    id: 'tree_canopy',
    label: 'Tree Canopy',
    description: 'Vegetation-based cooling intervention',
  },
  {
    id: 'cool_roof',
    label: 'Cool Roof',
    description: 'Reflective roof intervention',
  },
];

export default function MitigationPanel({ activeCityId, optimizationData, onOptimizationSuccess }: MitigationPanelProps) {
  const { data: mapData, isLoading: isMapLoading } = useCityMap(activeCityId);
  const optimizationMutation = useOptimizationMutation();

  const [budget, setBudget] = useState<number>(1000);
  const [selectedInterventions, setSelectedInterventions] = useState<Set<string>>(
    new Set(['tree_canopy', 'cool_roof'])
  );
  
  const [lastScenario, setLastScenario] = useState<{ budget: number; interventions: string[] } | null>(null);

  const isStale = useMemo(() => {
    if (!lastScenario || !optimizationData || optimizationData.cityId !== activeCityId) return false;
    const currentInterventions = Array.from(selectedInterventions).sort();
    const lastInterventions = [...lastScenario.interventions].sort();
    if (budget !== lastScenario.budget) return true;
    if (currentInterventions.length !== lastInterventions.length) return true;
    for (let i = 0; i < currentInterventions.length; i++) {
      if (currentInterventions[i] !== lastInterventions[i]) return true;
    }
    return false;
  }, [budget, selectedInterventions, lastScenario, optimizationData, activeCityId]);

  const hotspotIds = useMemo(() => {
    if (!mapData?.features) return [];
    return mapData.features
      .filter((f) => f.properties.hotspot_id)
      .map((f) => f.properties.feature_id);
  }, [mapData]);

  const toggleIntervention = (id: string) => {
    const next = new Set(selectedInterventions);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedInterventions(next);
  };

  const handleOptimize = () => {
    if (!activeCityId || hotspotIds.length === 0) return;
    
    optimizationMutation.mutate({
      city_id: activeCityId,
      hotspot_ids: hotspotIds,
      resource_budget: budget,
      interventions: Array.from(selectedInterventions),
    }, {
      onSuccess: (data) => {
        setLastScenario({
          budget,
          interventions: Array.from(selectedInterventions)
        });
        onOptimizationSuccess(data);
      }
    });
  };

  if (!activeCityId) {
    return (
      <div className="w-96 bg-zinc-900 border-r border-zinc-800 flex flex-col h-full text-zinc-100 p-6">
        <p className="text-zinc-400">Select a city to configure mitigation.</p>
      </div>
    );
  }

  const isFormValid = budget >= 0 && selectedInterventions.size > 0 && hotspotIds.length > 0;
  
  const activeData = optimizationData && optimizationData.cityId === activeCityId ? optimizationData.data : null;

  return (
    <div className="w-96 bg-zinc-900 border-r border-zinc-800 flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b border-zinc-800">
        <div className="flex items-center gap-3 mb-2">
          <ThermometerSun className="w-6 h-6 text-emerald-500" />
          <h2 className="text-xl font-semibold text-zinc-100 uppercase tracking-wider">Mitigation</h2>
        </div>
        <p className="text-sm text-zinc-400">
          Optimize interventions against identified heat-risk locations using a resource-constrained allocation model.
        </p>
      </div>

      <div className="p-6 flex flex-col gap-8 flex-1">
        {/* Hotspot Availability State */}
        {isMapLoading ? (
          <div className="text-sm text-zinc-400 animate-pulse">Loading region data...</div>
        ) : hotspotIds.length === 0 ? (
          <div className="bg-zinc-800/50 border border-zinc-700 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
            <p className="text-sm text-zinc-300">
              No canonical hotspots available for mitigation in this region.
            </p>
          </div>
        ) : (
          <>
            <div className="flex flex-col gap-1">
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                Available Hotspots
              </h3>
              <div className="text-sm text-zinc-300">
                <span className="font-semibold text-emerald-400">{hotspotIds.length}</span> canonical hotspots available
              </div>
            </div>

            {/* Scenario Configuration */}
            <div className="flex flex-col gap-6">
              {/* Resource Budget */}
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label htmlFor="budget" className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                    Resource Budget
                  </label>
                  <span className="text-sm font-bold text-emerald-400">
                    {budget.toLocaleString()} units
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <input
                    type="range"
                    min="0"
                    max="5000"
                    step="50"
                    value={budget}
                    onChange={(e) => setBudget(Number(e.target.value))}
                    className="flex-1 h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                    disabled={optimizationMutation.isPending}
                  />
                  <input
                    id="budget"
                    type="number"
                    min="0"
                    max="5000"
                    step="50"
                    value={budget}
                    onChange={(e) => setBudget(Number(e.target.value))}
                    className="w-20 bg-zinc-950 border border-zinc-700 rounded px-2 py-1.5 text-sm text-zinc-100 text-right focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 disabled:opacity-50"
                    disabled={optimizationMutation.isPending}
                  />
                </div>
              </div>

              {/* Interventions */}
              <div className="flex flex-col gap-3">
                <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                  Mitigation Strategies
                </label>
                {INTERVENTIONS.map((inv) => (
                  <button
                    key={inv.id}
                    onClick={() => toggleIntervention(inv.id)}
                    disabled={optimizationMutation.isPending}
                    className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-colors ${
                      selectedInterventions.has(inv.id)
                        ? 'border-emerald-500/50 bg-emerald-900/20'
                        : 'border-zinc-800 bg-zinc-800/30 hover:bg-zinc-800/50'
                    } ${optimizationMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className={`mt-0.5 flex shrink-0 items-center justify-center w-4 h-4 rounded border ${
                      selectedInterventions.has(inv.id)
                        ? 'bg-emerald-500 border-emerald-500 text-zinc-900'
                        : 'border-zinc-600 bg-zinc-900'
                    }`}>
                      {selectedInterventions.has(inv.id) && (
                        <svg className="w-3 h-3 fill-current" viewBox="0 0 20 20">
                          <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                        </svg>
                      )}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-zinc-200">{inv.label}</span>
                      <span className="text-xs text-zinc-500">{inv.description}</span>
                    </div>
                  </button>
                ))}
                {selectedInterventions.size === 0 && (
                  <div className="text-sm text-amber-500 mt-1">Select at least one mitigation strategy.</div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-zinc-800">
              <button
                onClick={handleOptimize}
                disabled={!isFormValid || optimizationMutation.isPending}
                className={`w-full py-2.5 rounded font-medium flex justify-center items-center gap-2 transition-colors
                  ${
                    optimizationMutation.isPending
                      ? 'bg-emerald-600/50 text-white cursor-wait'
                      : !isFormValid
                        ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                        : 'bg-emerald-600 hover:bg-emerald-500 text-white'
                  }`}
              >
                {optimizationMutation.isPending ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Optimizing...
                  </>
                ) : (
                  'Optimize Mitigation'
                )}
              </button>
            </div>
          </>
        )}

        {/* Results / Error Area */}
        {optimizationMutation.isError && (
          <div className="mt-2 bg-red-950/30 border border-red-900 rounded-lg p-4 flex flex-col gap-2">
            <div className="flex items-center gap-2 text-red-500 font-semibold text-sm">
              <ServerCrash className="w-4 h-4" />
              Optimization failed
            </div>
            <p className="text-xs text-red-400/80 break-words">
              {optimizationMutation.error?.message || 'An unknown error occurred while optimizing.'}
            </p>
          </div>
        )}

        {activeData && !optimizationMutation.isError && (
          <div className={`flex flex-col gap-4 ${isStale ? 'opacity-50' : ''}`}>
            <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              Optimization Result
            </h3>
            
            {isStale && (
              <div className="text-xs text-amber-500 bg-amber-950/30 p-2 rounded border border-amber-900">
                Scenario changed — run Optimize Mitigation to update recommendations.
              </div>
            )}
            
            {activeData.hotspot_allocations.length === 0 ? (
              <div className="text-sm text-zinc-400 bg-zinc-800/30 p-4 rounded-lg border border-zinc-800">
                No feasible mitigation allocation found for the selected scenario.
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-lg flex flex-col">
                  <span className="text-xs text-zinc-500 uppercase">Cooling Est.</span>
                  <span className="text-lg font-semibold text-zinc-200">
                    -{activeData.total_expected_cooling_celsius.toFixed(2)} °C
                  </span>
                </div>
                <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-lg flex flex-col">
                  <span className="text-xs text-zinc-500 uppercase">Resources Used</span>
                  <span className="text-lg font-semibold text-zinc-200">
                    {activeData.total_resources_used.toFixed(0)}
                  </span>
                </div>
                <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-lg flex flex-col col-span-2">
                  <span className="text-xs text-zinc-500 uppercase">Allocated Locations</span>
                  <span className="text-lg font-semibold text-zinc-200">
                    {activeData.hotspot_allocations.length}
                  </span>
                </div>
                {activeData.limiting_constraints && activeData.limiting_constraints.length > 0 && (
                   <div className="col-span-2 text-xs text-zinc-500 mt-2">
                     <span className="font-semibold">Constraints: </span>
                     {activeData.limiting_constraints.join(", ")}
                   </div>
                )}
                
                <div className="col-span-2 mt-4 flex flex-col gap-2">
                  <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-1">
                    Recommended Interventions
                  </h4>
                  {activeData.hotspot_allocations.map((alloc) => (
                    <div key={alloc.hotspot_id + alloc.intervention} className="bg-zinc-950/50 p-3 rounded border border-zinc-800 flex flex-col gap-2">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2 text-sm text-zinc-200 font-medium">
                          {alloc.intervention === 'tree_canopy' ? (
                            <TreePine className="w-4 h-4 text-emerald-500" />
                          ) : (
                            <Home className="w-4 h-4 text-sky-400" />
                          )}
                          {alloc.intervention === 'tree_canopy' ? 'Tree Canopy' : 'Cool Roof'}
                        </div>
                        <div className="text-xs font-mono text-zinc-500">{alloc.hotspot_id.split('_').slice(-1)[0]}</div>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-500">Allocation Intensity</span>
                        <span className="text-zinc-300 font-semibold">{alloc.intensity_allocated.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
