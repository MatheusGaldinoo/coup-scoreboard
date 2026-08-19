import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import TablePage from './pages/TablePage';
import LeaderboardPage from './pages/LeaderboardPage';
import MatchPage from './pages/MatchPage';

function Layout() {
  const location = useLocation();
  const isMatchPage = location.pathname.endsWith('/match');

  return (
    <div className="min-h-screen flex flex-col">
      {!isMatchPage && (
        <header className="py-6 px-4 md:px-8 flex justify-center border-b border-white/5 bg-surface/30 backdrop-blur-md sticky top-0 z-50">
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <span className="text-primary">Coup</span>
            <span className="text-text-muted font-light">Scoreboard</span>
          </h1>
        </header>
      )}

      <main className={`flex-1 w-full mx-auto animate-fade-in ${isMatchPage ? 'p-2 md:p-4 max-w-4xl' : 'max-w-7xl p-4 md:p-8'}`}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/:slug" element={<TablePage />} />
          <Route path="/:slug/leaderboard" element={<LeaderboardPage />} />
          <Route path="/:slug/match" element={<MatchPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout />
    </Router>
  );
}

export default App;
