"""
Enhanced chess engine module implementing Minimax algorithm with Alpha-Beta pruning.
Includes move ordering, iterative deepening, and advanced search techniques.
"""

import chess
from evaluation import evaluate_board


def order_moves(board: chess.Board, moves: list) -> list:
    """Order moves for better alpha-beta pruning efficiency."""
    def move_priority(move):
        priority = 0
        
        # Prioritize captures
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            moving_piece = board.piece_at(move.from_square)
            if captured_piece and moving_piece:
                # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
                piece_values = {
                    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
                    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
                }
                priority += piece_values[captured_piece.piece_type] * 10
                priority -= piece_values[moving_piece.piece_type]
        
        # Prioritize checks
        board.push(move)
        if board.is_check():
            priority += 50
        board.pop()
        
        # Prioritize promotions
        if move.promotion:
            priority += 800
        
        # Prioritize castling
        if board.is_castling(move):
            priority += 60
        
        # Prioritize center moves
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        if move.to_square in center_squares:
            priority += 20
        
        return priority
    
    return sorted(moves, key=move_priority, reverse=True)


def quiescence_search(board: chess.Board, alpha: int, beta: int, depth: int = 0) -> int:
    """Quiescence search to avoid horizon effect in tactical positions."""
    if depth > 10:  # Prevent infinite recursion
        return evaluate_board(board)
    
    # Stand pat evaluation
    stand_pat = evaluate_board(board)
    
    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    
    # Only search captures and checks in quiescence
    moves = []
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            moves.append(move)
    
    if not moves:
        return stand_pat
    
    # Order moves for better pruning
    moves = order_moves(board, moves)
    
    for move in moves:
        board.push(move)
        score = -quiescence_search(board, -beta, -alpha, depth + 1)
        board.pop()
        
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    
    return alpha


def search(board: chess.Board, depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
    """
    Minimax search with Alpha-Beta pruning.
    
    Args:
        board: Current chess board position
        depth: Search depth remaining
        alpha: Alpha value for pruning (best value maximizing player can guarantee)
        beta: Beta value for pruning (best value minimizing player can guarantee)
        maximizing_player: True if current player is maximizing, False if minimizing
        
    Returns:
        int: Evaluation score of the position
    """
    
    # Base case: if depth is 0 or game is over
    if board.is_game_over():
        return evaluate_board(board)
    
    if depth == 0:
        # Use quiescence search instead of static evaluation
        return quiescence_search(board, alpha, beta)
    
    # Get and order moves for better pruning
    moves = list(board.legal_moves)
    if not moves:
        return evaluate_board(board)
    
    moves = order_moves(board, moves)
    
    if maximizing_player:
        # Maximizing player tries to maximize the score
        max_eval = float('-inf')
        
        # Try all legal moves (now ordered)
        for move in moves:
            # Make the move
            board.push(move)
            
            # Recursively search with reduced depth and switch to minimizing player
            eval_score = search(board, depth - 1, alpha, beta, False)
            
            # Undo the move
            board.pop()
            
            # Update maximum evaluation
            max_eval = max(max_eval, eval_score)
            
            # Alpha-Beta pruning
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff - minimizing player won't choose this path
        
        return max_eval
    
    else:
        # Minimizing player tries to minimize the score
        min_eval = float('inf')
        
        # Try all legal moves (now ordered)
        for move in moves:
            # Make the move
            board.push(move)
            
            # Recursively search with reduced depth and switch to maximizing player
            eval_score = search(board, depth - 1, alpha, beta, True)
            
            # Undo the move
            board.pop()
            
            # Update minimum evaluation
            min_eval = min(min_eval, eval_score)
            
            # Alpha-Beta pruning
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff - maximizing player won't choose this path
        
        return min_eval


def iterative_deepening_search(board: chess.Board, max_depth: int, time_limit: float = None) -> chess.Move:
    """Iterative deepening search for better move ordering and time management."""
    import time
    
    start_time = time.time() if time_limit else None
    best_move = None
    
    # Search with increasing depth
    for depth in range(1, max_depth + 1):
        if time_limit and start_time:
            elapsed = time.time() - start_time
            if elapsed > time_limit:
                break
        
        try:
            current_best = find_best_move(board, depth)
            if current_best:
                best_move = current_best
        except:
            break
    
    return best_move or list(board.legal_moves)[0]


def find_best_move(board: chess.Board, depth: int) -> chess.Move:
    """
    Find the best move for the current position using enhanced Minimax with Alpha-Beta pruning.
    
    Args:
        board: Current chess board position
        depth: Search depth for the algorithm
        
    Returns:
        chess.Move: The best move found by the search algorithm
    """
    
    best_move = None
    max_eval = float('-inf')
    
    # Initialize alpha and beta for Alpha-Beta pruning
    alpha = float('-inf')
    beta = float('inf')
    
    # Get and order moves for better pruning
    moves = list(board.legal_moves)
    if not moves:
        return None
    
    moves = order_moves(board, moves)
    
    # Try all legal moves for the current position (now ordered)
    for move in moves:
        # Make the move
        board.push(move)
        
        # Search the resulting position with the opponent as maximizing player
        # (since we want to minimize the opponent's advantage)
        eval_score = search(board, depth - 1, alpha, beta, False)
        
        # Undo the move
        board.pop()
        
        # If this move gives a better evaluation, update best move
        if eval_score > max_eval:
            max_eval = eval_score
            best_move = move
        
        # Update alpha for pruning in subsequent iterations
        alpha = max(alpha, eval_score)
    
    return best_move
