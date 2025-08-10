"""
Enhanced evaluation module for chess engine.
Contains advanced board evaluation with material, positional, and tactical scoring.
"""

import chess
from config import (
    PAWN_VALUE, KNIGHT_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE, KING_VALUE,
    PAWN_PST, KNIGHT_PST, BISHOP_PST, ROOK_PST, QUEEN_PST, KING_PST,
    PAWN_PST_BLACK, KNIGHT_PST_BLACK, BISHOP_PST_BLACK, 
    ROOK_PST_BLACK, QUEEN_PST_BLACK, KING_PST_BLACK
)


def count_material(board: chess.Board, color: chess.Color) -> int:
    """Count total material value for a given color."""
    material = 0
    material += len(board.pieces(chess.PAWN, color)) * PAWN_VALUE
    material += len(board.pieces(chess.KNIGHT, color)) * KNIGHT_VALUE
    material += len(board.pieces(chess.BISHOP, color)) * BISHOP_VALUE
    material += len(board.pieces(chess.ROOK, color)) * ROOK_VALUE
    material += len(board.pieces(chess.QUEEN, color)) * QUEEN_VALUE
    return material


def evaluate_mobility(board: chess.Board) -> int:
    """Evaluate piece mobility (number of legal moves)."""
    current_player_mobility = len(list(board.legal_moves))
    
    # Switch turns to count opponent mobility
    board.push(chess.Move.null())
    opponent_mobility = len(list(board.legal_moves))
    board.pop()
    
    return (current_player_mobility - opponent_mobility) * 10


def evaluate_king_safety(board: chess.Board, color: chess.Color) -> int:
    """Evaluate king safety based on pawn shield and piece attacks."""
    king_square = board.king(color)
    if king_square is None:
        return -999999  # King captured
    
    safety_score = 0
    
    # Bonus for castling
    if board.has_castling_rights(color):
        if color == chess.WHITE:
            if board.has_kingside_castling_rights(color):
                safety_score += 50
            if board.has_queenside_castling_rights(color):
                safety_score += 30
        else:
            if board.has_kingside_castling_rights(color):
                safety_score += 50
            if board.has_queenside_castling_rights(color):
                safety_score += 30
    
    # Penalty for exposed king
    king_file = chess.square_file(king_square)
    king_rank = chess.square_rank(king_square)
    
    # Check pawn shield
    pawn_shield = 0
    if color == chess.WHITE:
        for file_offset in [-1, 0, 1]:
            shield_file = king_file + file_offset
            if 0 <= shield_file <= 7:
                shield_square = chess.square(shield_file, king_rank + 1)
                if board.piece_at(shield_square) == chess.Piece(chess.PAWN, chess.WHITE):
                    pawn_shield += 30
    else:
        for file_offset in [-1, 0, 1]:
            shield_file = king_file + file_offset
            if 0 <= shield_file <= 7:
                shield_square = chess.square(shield_file, king_rank - 1)
                if board.piece_at(shield_square) == chess.Piece(chess.PAWN, chess.BLACK):
                    pawn_shield += 30
    
    safety_score += pawn_shield
    
    # Penalty for being in check
    if board.is_check():
        safety_score -= 50
    
    return safety_score


def evaluate_pawn_structure(board: chess.Board) -> int:
    """Evaluate pawn structure (doubled, isolated, passed pawns)."""
    score = 0
    
    for color in [chess.WHITE, chess.BLACK]:
        multiplier = 1 if color == chess.WHITE else -1
        pawns = board.pieces(chess.PAWN, color)
        
        # Count pawns per file
        files = [0] * 8
        for pawn_square in pawns:
            files[chess.square_file(pawn_square)] += 1
        
        # Penalty for doubled pawns
        for file_count in files:
            if file_count > 1:
                score += multiplier * (file_count - 1) * -20
        
        # Penalty for isolated pawns
        for file_idx, file_count in enumerate(files):
            if file_count > 0:
                has_neighbor = False
                if file_idx > 0 and files[file_idx - 1] > 0:
                    has_neighbor = True
                if file_idx < 7 and files[file_idx + 1] > 0:
                    has_neighbor = True
                if not has_neighbor:
                    score += multiplier * -15  # Isolated pawn penalty
        
        # Bonus for passed pawns
        for pawn_square in pawns:
            file = chess.square_file(pawn_square)
            rank = chess.square_rank(pawn_square)
            
            is_passed = True
            if color == chess.WHITE:
                # Check if any black pawns block this pawn's path
                for check_rank in range(rank + 1, 8):
                    for check_file in [file - 1, file, file + 1]:
                        if 0 <= check_file <= 7:
                            check_square = chess.square(check_file, check_rank)
                            if board.piece_at(check_square) == chess.Piece(chess.PAWN, chess.BLACK):
                                is_passed = False
                                break
                    if not is_passed:
                        break
            else:
                # Check if any white pawns block this pawn's path
                for check_rank in range(rank - 1, -1, -1):
                    for check_file in [file - 1, file, file + 1]:
                        if 0 <= check_file <= 7:
                            check_square = chess.square(check_file, check_rank)
                            if board.piece_at(check_square) == chess.Piece(chess.PAWN, chess.WHITE):
                                is_passed = False
                                break
                    if not is_passed:
                        break
            
            if is_passed:
                # Bonus increases as pawn gets closer to promotion
                if color == chess.WHITE:
                    bonus = (rank - 1) * 20
                else:
                    bonus = (6 - rank) * 20
                score += multiplier * bonus
    
    return score


def evaluate_board(board: chess.Board) -> int:
    """
    Evaluate the current board position from the perspective of the current player.
    
    Args:
        board: The chess board to evaluate
        
    Returns:
        int: Evaluation score in centipawns (positive = good for current player)
    """
    
    # Check for game over conditions
    if board.is_checkmate():
        # If current player is in checkmate, they lose
        return -999999
    
    if board.is_stalemate() or board.is_insufficient_material() or board.is_repetition():
        # Draw conditions
        return 0
    
    # Initialize evaluation components
    evaluation = 0
    
    # 1. MATERIAL EVALUATION
    white_material = count_material(board, chess.WHITE)
    black_material = count_material(board, chess.BLACK)
    material_balance = white_material - black_material
    
    # 2. POSITIONAL EVALUATION (Piece-Square Tables)
    white_positional = 0
    black_positional = 0
    
    # Define piece-square tables for both colors
    white_psts = {
        chess.PAWN: PAWN_PST,
        chess.KNIGHT: KNIGHT_PST,
        chess.BISHOP: BISHOP_PST,
        chess.ROOK: ROOK_PST,
        chess.QUEEN: QUEEN_PST,
        chess.KING: KING_PST
    }
    
    black_psts = {
        chess.PAWN: PAWN_PST_BLACK,
        chess.KNIGHT: KNIGHT_PST_BLACK,
        chess.BISHOP: BISHOP_PST_BLACK,
        chess.ROOK: ROOK_PST_BLACK,
        chess.QUEEN: QUEEN_PST_BLACK,
        chess.KING: KING_PST_BLACK
    }
    
    # Calculate positional scores
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            if piece.color == chess.WHITE:
                white_positional += white_psts[piece.piece_type][square]
            else:
                black_positional += black_psts[piece.piece_type][square]
    
    positional_balance = white_positional - black_positional
    
    # 3. MOBILITY EVALUATION (only if not too expensive)
    try:
        mobility_score = evaluate_mobility(board)
    except:
        mobility_score = 0
    
    # 4. KING SAFETY EVALUATION
    white_king_safety = evaluate_king_safety(board, chess.WHITE)
    black_king_safety = evaluate_king_safety(board, chess.BLACK)
    king_safety_balance = white_king_safety - black_king_safety
    
    # 5. PAWN STRUCTURE EVALUATION
    pawn_structure_score = evaluate_pawn_structure(board)
    
    # 6. TACTICAL BONUSES
    tactical_bonus = 0
    
    # Bonus for controlling center squares
    center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
    for square in center_squares:
        if board.is_attacked_by(chess.WHITE, square):
            tactical_bonus += 10
        if board.is_attacked_by(chess.BLACK, square):
            tactical_bonus -= 10
    
    # Bishop pair bonus
    white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
    black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))
    if white_bishops >= 2:
        tactical_bonus += 30
    if black_bishops >= 2:
        tactical_bonus -= 30
    
    # COMBINE ALL EVALUATION COMPONENTS
    evaluation = (
        material_balance +           # Material advantage
        positional_balance +         # Piece placement
        mobility_score +             # Piece mobility
        king_safety_balance +        # King safety
        pawn_structure_score +       # Pawn structure
        tactical_bonus               # Tactical elements
    )
    
    # Return evaluation from the perspective of the current player
    if board.turn == chess.WHITE:
        return evaluation
    else:
        return -evaluation
