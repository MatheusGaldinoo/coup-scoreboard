import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Trophy, Users, PlayCircle, UserPlus, RefreshCcw } from 'lucide-react';
import api from '../api';

export default function TablePage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [table, setTable] = useState<any>(null);
  const [players, setPlayers] = useState<any[]>([]);
  const [activeMatch, setActiveMatch] = useState<any>(null);
  const [newPlayerName, setNewPlayerName] = useState('');
  const [selectedPlayers, setSelectedPlayers] = useState<string[]>([]);

  const [loading, setLoading] = useState(true);

  const fetchTableData = async () => {
    try {
      const [tableRes, playersRes, matchRes] = await Promise.allSettled([
        api.get(`/tables/${slug}`),
        api.get(`/tables/${slug}/players`),
        api.get(`/tables/${slug}/matches/active`)
      ]);

      if (tableRes.status === 'fulfilled') setTable(tableRes.value.data);
      if (playersRes.status === 'fulfilled') setPlayers(playersRes.value.data);
      if (matchRes.status === 'fulfilled' && matchRes.value.data) {
        setActiveMatch(matchRes.value.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTableData();
  }, [slug]);

  const handleAddPlayer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPlayerName.trim()) return;
    try {
      await api.post(`/tables/${slug}/players`, { name: newPlayerName });
      setNewPlayerName('');
      fetchTableData();
    } catch (e) {
      alert("Erro ao adicionar jogador");
    }
  };

  const togglePlayerSelection = (id: string) => {
    if (selectedPlayers.includes(id)) {
      setSelectedPlayers(selectedPlayers.filter(p => p !== id));
    } else {
      setSelectedPlayers([...selectedPlayers, id]);
    }
  };

  const handleStartMatch = async () => {
    if (selectedPlayers.length < 4 || selectedPlayers.length > 6) {
      alert("Selecione entre 4 e 6 jogadores para iniciar.");
      return;
    }
    try {
      await api.post(`/tables/${slug}/matches`, { player_ids: selectedPlayers });
      navigate(`/${slug}/match`);
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erro ao iniciar partida");
    }
  };

  if (loading) return <div className="text-center mt-20 animate-pulse">Carregando...</div>;
  if (!table) return <div className="text-center mt-20 text-danger">Mesa não encontrada.</div>;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header section */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-surface/50 p-6 rounded-2xl border border-white/5">
        <div>
          <h2 className="text-3xl font-bold">{table.name}</h2>
          <p className="text-text-muted text-sm mt-1">/{slug}</p>
        </div>
        <div className="flex gap-3">
          <Link to={`/${slug}/leaderboard`} className="btn btn-secondary gap-2">
            <Trophy size={18} className="text-primary" /> Leaderboard
          </Link>
          {activeMatch && (
            <Link to={`/${slug}/match`} className="btn btn-primary gap-2 animate-pulse">
              <PlayCircle size={18} /> Partida em Andamento
            </Link>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Adicionar Jogador */}
        <div className="glass-panel p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <UserPlus size={20} className="text-secondary" />
            Novo Jogador
          </h3>
          <form onSubmit={handleAddPlayer} className="space-y-3">
            <input
              type="text"
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
              placeholder="Nome do jogador..."
              className="w-full bg-surface-hover/50 border border-white/10 rounded-xl px-4 py-2 text-text placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-secondary/50"
            />
            <button type="submit" disabled={!newPlayerName.trim()} className="w-full btn bg-secondary/20 text-secondary hover:bg-secondary/30">
              Adicionar
            </button>
          </form>
        </div>

        {/* Jogadores cadastrados */}
        <div className="md:col-span-2 glass-panel p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Users size={20} className="text-primary" />
              Jogadores da Mesa
            </h3>
            <button onClick={fetchTableData} className="p-2 hover:bg-white/5 rounded-full transition-colors">
              <RefreshCcw size={16} className="text-text-muted" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {players.length === 0 ? (
              <p className="text-text-muted col-span-full">Nenhum jogador cadastrado ainda.</p>
            ) : (
              players.map(p => {
                const isSelected = selectedPlayers.includes(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => togglePlayerSelection(p.id)}
                    className={`flex items-center gap-2 p-3 border rounded-xl transition-all ${isSelected
                        ? 'border-primary bg-primary/10 text-primary font-medium'
                        : 'border-white/5 bg-surface-hover/30 hover:border-white/20 text-text-muted'
                      }`}
                  >
                    <div className={`w-3 h-3 rounded-full ${isSelected ? 'bg-primary' : 'bg-surface-hover border border-white/20'}`} />
                    {p.name}
                  </button>
                );
              })
            )}
          </div>

          {!activeMatch && players.length >= 4 && (
            <div className="mt-8 border-t border-white/5 pt-6 flex justify-between items-center">
              <p className="text-sm text-text-muted">
                {selectedPlayers.length} selecionados (Requer 4 a 6)
              </p>
              <button
                onClick={handleStartMatch}
                disabled={selectedPlayers.length < 4 || selectedPlayers.length > 6}
                className="btn btn-primary gap-2"
              >
                <PlayCircle size={20} /> Iniciar Partida
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
