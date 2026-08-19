import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Trophy, Crown, Target, Activity } from 'lucide-react';
import api from '../api';

export default function LeaderboardPage() {
  const { slug } = useParams();
  const [period, setPeriod] = useState('all');
  const [sortBy, setSortBy] = useState<'wins' | 'win_rate'>('wins');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/tables/${slug}/leaderboard?period=${period}`);
        setData(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, [slug, period]);

  // Ordenar rankings de acordo com o critério selecionado
  const sortedRankings = data?.rankings
    ? [...data.rankings].sort((a: any, b: any) => {
      if (sortBy === 'win_rate') return b.win_rate - a.win_rate;
      return b.wins - a.wins || b.total_kills - a.total_kills;
    })
    : [];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center flex-wrap gap-3">
        <Link to={`/${slug}`} className="btn bg-surface hover:bg-surface-hover gap-2 text-text-muted text-sm">
          <ArrowLeft size={16} /> Voltar
        </Link>
        <div className="flex gap-2 bg-surface/50 p-1 rounded-xl border border-white/5">
          {['all', 'monthly', 'weekly'].map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${period === p ? 'bg-primary text-background' : 'text-text-muted hover:text-text'
                }`}
            >
              {p === 'all' ? 'Geral' : p === 'monthly' ? 'Mês' : 'Semana'}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary/10 rounded-xl">
              <Trophy className="text-primary" size={24} />
            </div>
            <h2 className="text-2xl font-bold">Leaderboard</h2>
          </div>
          {/* Toggle de ordenação */}
          <div className="flex gap-1 bg-surface/50 p-1 rounded-xl border border-white/5">
            <button
              onClick={() => setSortBy('wins')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${sortBy === 'wins' ? 'bg-primary text-background' : 'text-text-muted hover:text-text'
                }`}
            >
              Vitórias
            </button>
            <button
              onClick={() => setSortBy('win_rate')}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${sortBy === 'win_rate' ? 'bg-primary text-background' : 'text-text-muted hover:text-text'
                }`}
            >
              Win Rate %
            </button>
          </div>
        </div>

        {loading ? (
          <div className="py-20 text-center text-text-muted animate-pulse">Calculando posições...</div>
        ) : (
          <div className="space-y-4">
            {sortedRankings.length === 0 && (
              <div className="py-10 text-center text-text-muted">Nenhum dado encontrado para o período selecionado.</div>
            )}

            {sortedRankings.map((player: any, index: number) => (
              <div key={player.player_id} className="flex items-center gap-4 bg-surface-hover/30 p-4 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg
                  ${index === 0 ? 'bg-gold/20 text-gold border border-gold/30' :
                    index === 1 ? 'bg-slate-400/20 text-slate-300 border border-slate-400/30' :
                      index === 2 ? 'bg-amber-700/20 text-amber-500 border border-amber-700/30' :
                        'bg-surface text-text-muted'}
                `}>
                  #{index + 1}
                </div>

                <div className="flex-1">
                  <h3 className="font-semibold text-lg flex items-center gap-2">
                    {player.player_name}
                    {index === 0 && <Crown size={16} className="text-gold" />}
                  </h3>
                  <div className="flex gap-4 text-sm text-text-muted mt-1">
                    <span title="Partidas Jogadas">{player.matches_played} partidas</span>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-right">
                  <div className="hidden sm:block">
                    <div className="flex items-center gap-1 justify-end text-text-muted text-sm">
                      <Target size={14} /> Kills
                    </div>
                    <div className="font-semibold">{player.total_kills}</div>
                  </div>
                  <div className="hidden sm:block">
                    <div className="flex items-center gap-1 justify-end text-text-muted text-sm">
                      <Activity size={14} /> Win Rate
                    </div>
                    <div className="font-semibold">{player.win_rate}%</div>
                  </div>
                  <div>
                    <div className="text-primary text-sm font-medium">
                      {sortBy === 'wins' ? 'Vitórias' : 'Taxa'}
                    </div>
                    <div className="font-bold text-xl">
                      {sortBy === 'wins' ? player.wins : `${player.win_rate}%`}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
