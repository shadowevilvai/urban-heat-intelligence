import { Map, Layers, ThermometerSun, Database } from 'lucide-react';

export type SidebarTab = 'map' | 'layers' | 'mitigation' | 'sources';

interface SidebarProps {
  activeTab: SidebarTab;
  onTabChange: (tab: SidebarTab) => void;
}

export default function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const tabs = [
    { id: 'map' as const, label: 'Heat Map', icon: Map },
    { id: 'layers' as const, label: 'Data Layers', icon: Layers },
    { id: 'mitigation' as const, label: 'Mitigation', icon: ThermometerSun },
    { id: 'sources' as const, label: 'Data Sources', icon: Database }
  ];

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col h-full hidden md:flex z-20">
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-sm font-semibold tracking-wider text-zinc-400 uppercase">Urban Heat Intel</h2>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {tabs.map(tab => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                isActive
                  ? 'bg-zinc-800 text-white'
                  : 'hover:bg-zinc-800/50 text-zinc-400'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-zinc-300' : ''}`} />
              <span className="font-medium text-sm">{tab.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="p-4 border-t border-zinc-800">
        <div className="text-xs text-zinc-500">
          <p>Mumbai AOI Active</p>
          <p className="mt-1">P1 Observational Data</p>
        </div>
      </div>
    </aside>
  );
}
