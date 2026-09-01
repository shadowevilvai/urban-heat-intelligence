import { useState, useEffect } from 'react';
import Header from './Header';
import Sidebar, { type SidebarTab } from './Sidebar';
import LayerPanel from '../layers/LayerPanel';
import MapEngine from '../map/MapEngine';
import FeaturePanel from '../panels/FeaturePanel';
import MitigationPanel from '../panels/MitigationPanel';
import { useCities } from '../../api/queries';
import type { OptimizeResponse } from '../../data/types';

export default function AppShell() {
  const [selectedFeatureId, setSelectedFeatureId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<SidebarTab>('layers');
  const [activeLayers, setActiveLayers] = useState<string[]>(['lst', 'hotspots']);
  const [activeCityId, setActiveCityId] = useState<string | null>(null);
  const [optimizationData, setOptimizationData] = useState<{cityId: string; data: OptimizeResponse} | null>(null);

  const { data: cities, isLoading: isCitiesLoading, isError: isCitiesError, error: citiesError } = useCities();

  const toggleLayer = (layerId: string) => {
    setActiveLayers(prev =>
      prev.includes(layerId)
        ? prev.filter(id => id !== layerId)
        : [...prev, layerId]
    );
  };

  useEffect(() => {
    // Set default city to 'mumbai' if available, otherwise first city in the list
    if (cities && cities.length > 0 && !activeCityId) {
      const mumbai = cities.find(c => c.city_id === 'mumbai');
      if (mumbai) {
        setActiveCityId(mumbai.city_id);
      } else {
        setActiveCityId(cities[0].city_id);
      }
    }
  }, [cities, activeCityId]);

  const handleCityChange = (cityId: string) => {
    setActiveCityId(cityId);
    setSelectedFeatureId(null); // Clear selected feature when city changes
    setOptimizationData(null);  // Clear P3 recommendations when city changes
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-zinc-900 text-zinc-100 overflow-hidden">
      <Header />
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          cities={cities}
          activeCityId={activeCityId}
          onCityChange={handleCityChange}
        />

        {activeTab === 'layers' && (
          <LayerPanel activeLayers={activeLayers} toggleLayer={toggleLayer} />
        )}

        {activeTab === 'mitigation' && (
          <MitigationPanel
            activeCityId={activeCityId}
            optimizationData={optimizationData}
            onOptimizationSuccess={(data) => {
              if (activeCityId) {
                setOptimizationData({ cityId: activeCityId, data });
              }
            }}
          />
        )}

        <main className="flex-1 relative h-full">
          {isCitiesLoading && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-zinc-900 bg-opacity-75">
              <div className="text-zinc-300 animate-pulse">Loading regions...</div>
            </div>
          )}

          {isCitiesError && (
            <div className="absolute inset-0 z-50 flex items-center justify-center bg-zinc-900 bg-opacity-75">
              <div className="text-red-400 bg-red-900/20 p-4 rounded-md border border-red-800">
                Failed to load regions. {citiesError?.message || 'Backend unavailable.'}
              </div>
            </div>
          )}

          {activeCityId && (
            <MapEngine
              activeCityId={activeCityId}
              activeLayers={activeLayers}
              onSelectFeatureId={setSelectedFeatureId}
              optimizationData={optimizationData}
            />
          )}

          {selectedFeatureId && activeCityId && (
            <div className="absolute top-4 right-4 z-20">
              <FeaturePanel
                activeCityId={activeCityId}
                featureId={selectedFeatureId}
                onClose={() => setSelectedFeatureId(null)}
                optimizationData={optimizationData}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
