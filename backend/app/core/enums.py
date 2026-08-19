from enum import Enum

class MatchStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class TurnPhase(str, Enum):
    AWAITING_ACTION = "awaiting_action"
    AWAITING_REACTION = "awaiting_reaction"
    AWAITING_CHALLENGE_RESULT = "awaiting_challenge_result"
    ACTION_BLOCKED = "action_blocked"
    AWAITING_BLOCK_CHALLENGE_RESULT = "awaiting_block_challenge_result"
    RESOLVING = "resolving"
    TURN_COMPLETE = "turn_complete"

class ActionType(str, Enum):
    INCOME = "income"              # +1 moeda
    FOREIGN_AID = "foreign_aid"    # +2 moedas
    COUP = "coup"                  # -7 moedas, -1 vida alvo
    TAX = "tax"                    # +3 moedas (Duque)
    STEAL = "steal"                # +2 moedas, -2 alvo (Capitão)
    ASSASSINATE = "assassinate"    # -3 moedas, -1 vida alvo (Assassino)
    EXCHANGE = "exchange"          # Sem efeito no app (Embaixador)

class EventType(str, Enum):
    ACTION = "action"                      # Ação de turno
    CHALLENGE = "challenge"                # Desafio a uma ação
    BLOCK = "block"                        # Bloqueio de uma ação
    CHALLENGE_BLOCK = "challenge_block"    # Desafio a um bloqueio
    LOSS_OF_LIFE = "loss_of_life"          # Alguém perdeu vida
    ELIMINATION = "elimination"            # Jogador eliminado (0 vidas)
    VICTORY = "victory"                    # Vencedor detectado
