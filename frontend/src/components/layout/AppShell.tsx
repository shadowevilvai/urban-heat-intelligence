import { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import MapEngine from '../map/MapEngine';
import FeaturePanel from '../panels/FeaturePanel';
import type { SpatialFeature } from '../../data/types';

export default function AppShell() {
  const [selectedFeature, setSelectedFeature] = useState<SpatialFeature | null>(null);

  return (
    <div className="flex flex-col h-screen w-screen bg-zinc-900 text-zinc-100 overflow-hidden">
      <Header />
      <div className="flex flex-1 overflow-hidden relative">
        <Sidebar />
        <main className="flex-1 relative h-full">
          <MapEngine onSelectFeature={setSelectedFeature} />
          {selectedFeature && (
            <div className="absolute top-4 right-4 z-10">
              <FeaturePanel feature={selectedFeature} onClose={() => setSelectedFeature(null)} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
