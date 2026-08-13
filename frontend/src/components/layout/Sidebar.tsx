import { Map, Layers, ThermometerSun, Database } from 'lucide-react';

export default function Sidebar() {
  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col h-full hidden md:flex">
      <div className="p-4 border-b border-zinc-800">
        <h2 className="text-sm font-semibold tracking-wider text-zinc-400 uppercase">Urban Heat Intel</h2>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md bg-zinc-800 text-white">
          <Map className="w-5 h-5 text-zinc-400" />
          <span className="font-medium text-sm">Heat Map</span>
        </a>
        <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800/50 text-zinc-400 transition-colors">
          <Layers className="w-5 h-5" />
          <span className="font-medium text-sm">Data Layers</span>
        </a>
        <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800/50 text-zinc-400 transition-colors">
          <ThermometerSun className="w-5 h-5" />
          <span className="font-medium text-sm">Mitigation</span>
        </a>
        <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800/50 text-zinc-400 transition-colors">
          <Database className="w-5 h-5" />
          <span className="font-medium text-sm">Data Sources</span>
        </a>
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
