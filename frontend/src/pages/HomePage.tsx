import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlusCircle, Users } from 'lucide-react';
import api from '../api';

export default function HomePage() {
  const [tableName, setTableName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleCreateTable = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tableName.trim()) return;

    try {
      setIsLoading(true);
      setError('');
      const response = await api.post('/tables', { name: tableName });
      const slug = response.data.slug;
      navigate(`/${slug}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar a mesa. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-12 md:mt-24">
      <div className="glass-panel p-8 text-center animate-slide-up">
        <div className="w-16 h-16 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Users size={32} />
        </div>

        <h2 className="text-3xl font-bold mb-2">Bem-vindo ao Coup Scoreboard</h2>
        <p className="text-text-muted mb-8 text-lg">
          Acompanhe moedas, vidas e mantenha um ranking global da sua liga local.
        </p>

        <form onSubmit={handleCreateTable} className="space-y-4">
          <div className="text-left">
            <label htmlFor="tableName" className="block text-sm font-medium text-text-muted mb-1 ml-1">
              Nome da nova mesa (ex: Firma, Família)
            </label>
            <input
              id="tableName"
              type="text"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              placeholder="Digite o nome da mesa"
              className="w-full bg-surface-hover/50 border border-white/10 rounded-xl px-4 py-3 text-text placeholder-white/20 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
              required
              disabled={isLoading}
            />
          </div>

          {error && <p className="text-danger text-sm text-left ml-1">{error}</p>}

          <button
            type="submit"
            disabled={isLoading || !tableName.trim()}
            className="w-full btn btn-primary py-3 text-lg flex items-center justify-center gap-2 mt-4"
          >
            <PlusCircle size={20} />
            {isLoading ? 'Criando...' : 'Criar Nova Mesa'}
          </button>
        </form>
      </div>

      <p className="text-center text-text-muted/50 mt-8 text-sm">
        O Coup Scoreboard não substitui o baralho. Ele é um assistente para o operador da partida.
      </p>
    </div>
  );
}
