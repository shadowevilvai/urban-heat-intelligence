import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppShell from './components/layout/AppShell';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  );
}

export default App;
