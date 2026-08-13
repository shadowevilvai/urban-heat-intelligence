export default function Header() {
  return (
    <header className="h-14 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between px-4 z-20 md:hidden">
      <div className="flex items-center gap-2">
        <h1 className="text-base font-semibold text-white tracking-wide">Urban Heat Intelligence</h1>
      </div>
    </header>
  );
}
