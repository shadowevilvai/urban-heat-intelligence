import { useState } from 'react';
import Header from './Header';
import Sidebar, { type SidebarTab } from './Sidebar';
import LayerPanel from '../layers/LayerPanel';
import MapEngine from '../map/MapEngine';
import FeaturePanel from '../panels/FeaturePanel';
import type { SpatialFeature } from '../../data/types';

export default function AppShell() {
  const [selectedFeature, setSelectedFeature] = useState<SpatialFeature | null>(null);
  const [activeTab, setActiveTab] = useState<SidebarTab>('layers');
  const [activeLayer, setActiveLayer] = useState<string | null>('lst');

  return (
    <div className="flex flex-col h-screen w-screen bg-zinc-900 text-zinc-100 overflow-hidden">
      <Header />
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === 'layers' && (
          <LayerPanel activeLayer={activeLayer} setActiveLayer={setActiveLayer} />
        )}

        <main className="flex-1 relative h-full">
          <MapEngine activeLayerId={activeLayer} onSelectFeature={setSelectedFeature} />
          {selectedFeature && (
            <div className="absolute top-4 right-4 z-20">
              <FeaturePanel feature={selectedFeature} onClose={() => setSelectedFeature(null)} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
