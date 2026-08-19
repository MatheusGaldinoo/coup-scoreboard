import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, CircleDollarSign, Heart, HeartOff, Skull, ShieldAlert, Swords, Handshake, Landmark, ArrowLeftRight, Crosshair, XCircle, CirclePlus, Eye, Hand, HandCoins, Sword } from 'lucide-react';
import api from '../api';

// Cores únicas por jogador (até 6)
const PLAYER_COLORS = [
  { bg: 'bg-blue-500/15', ring: 'ring-blue-400', text: 'text-blue-400', border: 'border-blue-500/30', accent: 'bg-blue-500' },
  { bg: 'bg-purple-500/15', ring: 'ring-purple-400', text: 'text-purple-400', border: 'border-purple-500/30', accent: 'bg-purple-500' },
  { bg: 'bg-emerald-500/15', ring: 'ring-emerald-400', text: 'text-emerald-400', border: 'border-emerald-500/30', accent: 'bg-emerald-500' },
  { bg: 'bg-rose-500/15', ring: 'ring-rose-400', text: 'text-rose-400', border: 'border-rose-500/30', accent: 'bg-rose-500' },
  { bg: 'bg-amber-500/15', ring: 'ring-amber-400', text: 'text-amber-400', border: 'border-amber-500/30', accent: 'bg-amber-500' },
  { bg: 'bg-cyan-500/15', ring: 'ring-cyan-400', text: 'text-cyan-400', border: 'border-cyan-500/30', accent: 'bg-cyan-500' },
];

// Mapa de ação -> nome PT-BR + ícone
const ACTION_MAP: Record<string, { label: string; icon: React.ReactNode; showLabel: boolean }> = {
  income: { label: 'Renda', showLabel: false, icon: <CircleDollarSign size={24} className="text-gold" /> },
  foreign_aid: { 
    label: 'Ajuda Externa', 
    showLabel: false, 
    icon: (
      <div className="flex -space-x-2">
        <CircleDollarSign size={24} className="text-gold" />
        <CircleDollarSign size={24} className="text-gold" />
      </div>
    ) 
  },
  coup: { label: 'Golpe de Estado', showLabel: true, icon: null },
  tax: { 
    label: 'Taxa', 
    showLabel: false, 
    icon: (
      <div className="flex items-center gap-1 text-primary">
        <HandCoins size={24} />
        <div className="flex -space-x-1">
          <CircleDollarSign size={16} className="text-gold" />
          <CircleDollarSign size={16} className="text-gold" />
          <CircleDollarSign size={16} className="text-gold" />
        </div>
      </div>
    ) 
  },
  steal: { 
    label: 'Roubar', 
    showLabel: false, 
    icon: (
      <div className="flex items-center gap-1 text-secondary">
        <Hand size={24} />
        <div className="flex -space-x-1">
          <CircleDollarSign size={16} className="text-gold" />
          <CircleDollarSign size={16} className="text-gold" />
        </div>
      </div>
    ) 
  },
  assassinate: { 
    label: 'Assassinar', 
    showLabel: false, 
    icon: (
      <div className="flex items-center gap-1 text-danger">
        <Skull size={24} />
        <Sword size={24} />
      </div>
    ) 
  },
  exchange: { 
    label: 'Trocar', 
    showLabel: false, 
    icon: (
      <div className="flex items-center gap-1 text-purple-400">
        <ArrowLeftRight size={24} />
        <Eye size={24} />
      </div>
    ) 
  },
};

const getActionLabel = (key: string) => ACTION_MAP[key]?.label || key;

export default function MatchPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [match, setMatch] = useState<any>(null);
  const [players, setPlayers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [selectedTargetId, setSelectedTargetId] = useState<string | null>(null);

  const fetchMatch = async () => {
    try {
      const [matchRes, playersRes] = await Promise.all([
        api.get(`/tables/${slug}/matches/active`),
        api.get(`/tables/${slug}/players`)
      ]);
      setMatch(matchRes.data);
      setPlayers(playersRes.data);
    } catch (e: any) {
      if (e.response?.status === 404) {
        navigate(`/${slug}`);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatch();
    const interval = setInterval(fetchMatch, 3000);
    return () => clearInterval(interval);
  }, [slug]);

  const getPlayerName = (id: string) => players.find(p => p.id === id)?.name || 'Desconhecido';

  const handleDeclareAction = async () => {
    if (!selectedAction) return;
    try {
      await api.post(`/matches/${match.id}/actions/declare?actor_id=${match.current_turn_player_id}`, {
        action_type: selectedAction,
        target_id: selectedTargetId
      });
      setSelectedAction(null);
      setSelectedTargetId(null);
      fetchMatch();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Erro ao fazer ação");
    }
  };

  const handleReaction = async (reactionType: 'pass' | 'block' | 'challenge', actorId?: string) => {
    try {
      if (reactionType === 'pass') {
        await api.post(`/matches/${match.id}/actions/allow`);
      } else if (reactionType === 'challenge') {
        await api.post(`/matches/${match.id}/actions/challenge?challenger_id=${actorId}`);
      } else if (reactionType === 'block') {
        await api.post(`/matches/${match.id}/actions/block?blocker_id=${actorId}`);
      }
      fetchMatch();
    } catch (e: any) {
      alert(e.response?.data?.detail);
    }
  };

  const handleChallengeBlock = async (challenge: boolean, challengerId?: string) => {
    try {
      if (!challenge) {
        await api.post(`/matches/${match.id}/actions/allow`);
      } else {
        await api.post(`/matches/${match.id}/actions/challenge-block?challenger_id=${challengerId}`);
      }
      fetchMatch();
    } catch (e: any) {
      alert(e.response?.data?.detail);
    }
  };

  const handleResolveChallenge = async (loserId: string) => {
    try {
      await api.post(`/matches/${match.id}/actions/resolve-challenge?loser_id=${loserId}`);
      fetchMatch();
    } catch (e: any) {
      alert(e.response?.data?.detail);
    }
  };

  const handleLoseLife = async (loserId: string) => {
    try {
      await api.post(`/matches/${match.id}/actions/lose-life?target_id=${loserId}`);
      fetchMatch();
    } catch (e: any) {
      alert(e.response?.data?.detail);
    }
  };

  const handleNextTurn = async () => {
    try {
      await api.post(`/matches/${match.id}/actions/next-turn`);
      fetchMatch();
    } catch (e: any) {
      alert(e.response?.data?.detail);
    }
  };

  const handleAbortMatch = async () => {
    if (!confirm('Tem certeza que deseja abortar a partida? Esta ação não pode ser desfeita.')) return;
    try {
      await api.post(`/tables/${slug}/matches/${match.id}/cancel`);
      navigate(`/${slug}`);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Erro ao abortar partida');
    }
  };

  if (loading) return <div className="text-center mt-20 animate-pulse">Sincronizando Partida...</div>;
  if (!match) return null;

  const currentTurnName = getPlayerName(match.current_turn_player_id);
  const isAwaitingAction = match.turn_phase === 'awaiting_action';
  const isAwaitingReaction = match.turn_phase === 'awaiting_reaction';
  const isActionBlocked = match.turn_phase === 'action_blocked';
  const isAwaitingChallengeResult = match.turn_phase === 'awaiting_challenge_result';
  const isAwaitingBlockChallengeResult = match.turn_phase === 'awaiting_block_challenge_result';
  const isResolving = match.turn_phase === 'resolving';
  const isChallengePhase = isAwaitingChallengeResult || isAwaitingBlockChallengeResult;

  const sortedParts = [...match.participations].sort((a: any, b: any) => a.turn_order - b.turn_order);
  const aliveParts = sortedParts.filter((p: any) => !p.is_eliminated);

  // Renderizar corações: 2 corações, preenchidos ou ocos
  const renderHearts = (lives: number) => (
    <div className="flex gap-1">
      {[0, 1].map(i => (
        i < lives
          ? <Heart key={i} size={18} className="text-danger fill-danger" />
          : <HeartOff key={i} size={18} className="text-danger/30" />
      ))}
    </div>
  );

  return (
    <div className="space-y-4 max-w-4xl mx-auto pb-52">
      {/* Header compacto: turno + vez na mesma linha */}
      <div className="flex justify-between items-center bg-surface/50 px-4 py-2.5 rounded-xl border border-white/5">
        <Link to={`/${slug}`} className="text-text-muted hover:text-text transition-colors">
          <ArrowLeft size={18} />
        </Link>
        <div className="font-medium text-sm flex items-center gap-2">
          <span className="text-text-muted">Turno {match.turn_number}</span>
          <span className="text-white/20">·</span>
          <span className="text-primary">Vez de {currentTurnName}</span>
        </div>
        <button onClick={handleAbortMatch} className="text-danger/60 hover:text-danger transition-colors" title="Abortar partida">
          <XCircle size={18} />
        </button>
      </div>

      {/* Grid de Jogadores */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {sortedParts.map((p: any) => {
          const isTurn = match.current_turn_player_id === p.player_id;
          const isTarget = selectedTargetId === p.player_id;
          const color = PLAYER_COLORS[p.turn_order % PLAYER_COLORS.length];

          if (p.is_eliminated) {
            return (
              <div key={p.id} className="glass-panel p-4 opacity-30 grayscale flex flex-col items-center justify-center">
                <Skull size={28} className="mb-1.5" />
                <span className="font-bold text-sm line-through">{getPlayerName(p.player_id)}</span>
              </div>
            );
          }

          return (
            <div
              key={p.id}
              onClick={() => isAwaitingAction && !isTurn && setSelectedTargetId(p.player_id)}
              className={`relative glass-panel p-4 cursor-pointer transition-all ${color.bg} ${isTurn ? `ring-2 ${color.ring} scale-[1.03]` : ''
                } ${isTarget ? 'ring-2 ring-danger bg-danger/10' : ''}`}
            >
              {/* Nome do jogador aumentado */}
              <div className={`text-center font-bold text-2xl mb-3 ${color.text}`}>{getPlayerName(p.player_id)}</div>
              <div className="flex justify-around items-center">
                <div className="flex items-center gap-1.5">
                  <CircleDollarSign size={18} className="text-gold" />
                  <span className="font-bold">{p.coins}</span>
                </div>
                {renderHearts(p.lives)}
              </div>

              {/* Botões de reação nos cards - Visibilidade Melhorada */}
              {(!isAwaitingAction && !isResolving && !isChallengePhase && !isTurn) && (
                <div className="mt-4 flex gap-2 justify-center flex-wrap">
                  {isAwaitingReaction && (
                    <button onClick={(e) => { e.stopPropagation(); handleReaction('challenge', p.player_id); }} className="text-sm font-bold bg-danger text-white px-3 py-1.5 rounded-xl shadow-lg shadow-danger/20 hover:scale-105 transition-transform">Desafiar</button>
                  )}
                  {isAwaitingReaction && match.pending_target_id === p.player_id && (
                    <button onClick={(e) => { e.stopPropagation(); handleReaction('block', p.player_id); }} className="text-sm font-bold bg-secondary text-white px-3 py-1.5 rounded-xl shadow-lg shadow-secondary/20 hover:scale-105 transition-transform">Bloquear</button>
                  )}
                  {isActionBlocked && match.pending_target_id !== p.player_id && (
                    <button onClick={(e) => { e.stopPropagation(); handleChallengeBlock(true, p.player_id); }} className="text-sm font-bold bg-danger text-white px-3 py-1.5 rounded-xl shadow-lg shadow-danger/20 hover:scale-105 transition-transform">D. Bloqueio</button>
                  )}
                </div>
              )}

              {/* Botão Perder Vida durante Desafio ou Resolução */}
              {((isResolving && match.pending_target_id === p.player_id) || isChallengePhase) && (
                <div className="mt-4 flex justify-center">
                  <button onClick={(e) => {
                    e.stopPropagation();
                    if (isChallengePhase) {
                      handleResolveChallenge(p.player_id);
                    }
                    handleLoseLife(p.player_id);
                  }} className="text-sm font-bold bg-danger text-white px-4 py-2 rounded-xl w-full flex items-center justify-center gap-2 shadow-lg shadow-danger/20 hover:scale-105 transition-transform">
                    <Skull size={16} /> Perder Vida
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action Bar */}
      <div className="fixed bottom-4 left-4 right-4 md:left-1/2 md:-translate-x-1/2 md:w-full max-w-2xl bg-surface-hover/90 backdrop-blur-xl border border-white/10 p-4 rounded-3xl shadow-2xl z-50">

        {isAwaitingAction && (
          <div className="space-y-3">
            <div className="text-center text-sm text-primary font-medium">O que {currentTurnName} fará?</div>
            <div className="flex flex-col gap-3">
              <div className="flex flex-wrap gap-2 justify-center pb-3 border-b border-white/5">
                {['income', 'foreign_aid', 'coup'].map(key => {
                  const { label, icon, showLabel } = ACTION_MAP[key];
                  return (
                    <button
                      key={key}
                      onClick={() => setSelectedAction(key)}
                      className={`flex items-center justify-center min-h-[44px] px-4 py-2 rounded-xl text-sm font-bold transition-colors ${selectedAction === key ? 'bg-primary text-background shadow-lg shadow-primary/20' : 'bg-surface text-text hover:bg-white/10 border border-white/5'
                        }`}
                      title={label}
                    >
                      {showLabel ? label : icon}
                    </button>
                  );
                })}
              </div>
              <div className="flex flex-wrap gap-2 justify-center">
                {['tax', 'steal', 'assassinate', 'exchange'].map(key => {
                  const { label, icon, showLabel } = ACTION_MAP[key];
                  return (
                    <button
                      key={key}
                      onClick={() => setSelectedAction(key)}
                      className={`flex items-center justify-center min-h-[44px] px-4 py-2 rounded-xl text-sm font-bold transition-colors ${selectedAction === key ? 'bg-primary text-background shadow-lg shadow-primary/20' : 'bg-surface text-text hover:bg-white/10 border border-white/5'
                        }`}
                      title={label}
                    >
                      {showLabel ? label : icon}
                    </button>
                  );
                })}
              </div>
            </div>

            {selectedAction && (
              <div className="flex items-center justify-between p-3 bg-background/50 rounded-xl">
                <div className="text-sm">
                  Ação: <span className="font-bold text-primary">{getActionLabel(selectedAction)}</span>
                  {selectedTargetId && <span> → <span className="font-bold text-danger">{getPlayerName(selectedTargetId)}</span></span>}
                </div>
                <button onClick={handleDeclareAction} className="btn btn-primary py-1 px-4 text-sm">
                  Confirmar
                </button>
              </div>
            )}
          </div>
        )}

        {isAwaitingReaction && (
          <div className="text-center space-y-3">
            <div className="text-sm font-medium flex items-center justify-center gap-2">
              <ShieldAlert size={16} className="text-primary" />
              {currentTurnName} usou <span className="text-primary font-bold">{getActionLabel(match.pending_action)}</span>
              {match.pending_target_id && <span> em <span className="text-danger">{getPlayerName(match.pending_target_id)}</span></span>}
            </div>
            <p className="text-xs text-text-muted">Use os botões nos cards para reagir, ou passe.</p>
            <button onClick={() => handleReaction('pass')} className="btn btn-secondary w-full text-sm">
              Ninguém reagiu (Passar)
            </button>
          </div>
        )}

        {isActionBlocked && (
          <div className="text-center space-y-3">
            <div className="text-secondary text-sm font-medium flex items-center justify-center gap-2">
              <ShieldAlert size={16} />
              {getPlayerName(match.pending_target_id)} BLOQUEOU {getActionLabel(match.pending_action)}
            </div>
            <button onClick={() => handleChallengeBlock(false)} className="btn btn-secondary w-full text-sm">
              Aceitar Bloqueio (Passar)
            </button>
          </div>
        )}

        {isChallengePhase && (
          <div className="text-center space-y-3">
            <div className="text-danger text-sm font-bold flex items-center justify-center gap-2">
              <Swords size={16} />
              DESAFIO LANÇADO!
            </div>
            <p className="text-xs text-text-muted">Clique em "Perder Vida" no jogador que perdeu o desafio.</p>
          </div>
        )}

        {isResolving && (
          <div className="text-center space-y-3">
            <p className="text-xs text-text-muted">Se necessário, aplique "Perder Vida" no alvo antes de avançar.</p>
            <button onClick={handleNextTurn} className="btn btn-primary w-full text-sm font-bold">
              Próximo Turno
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
