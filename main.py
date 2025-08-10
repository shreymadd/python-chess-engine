"""
Main module for the chess engine.
Provides a command-line interface for playing chess against the AI.
"""

import chess
import time
from engine import find_best_move, iterative_deepening_search


def print_board_with_coordinates(board):
    """Print the board with file and rank coordinates for better readability."""
    print("\n  a b c d e f g h")
    print("  ---------------")
    
    board_str = str(board)
    lines = board_str.split('\n')
    
    for i, line in enumerate(lines):
        rank = 8 - i
        print(f"{rank}|{line}|{rank}")
    
    print("  ---------------")
    print("  a b c d e f g h\n")


def get_user_move(board):
    """
    Get a valid move from the user in UCI format (e.g., 'e2e4').
    
    Args:
        board: Current chess board position
        
    Returns:
        chess.Move: Valid move entered by the user
    """
    while True:
        try:
            # Show some helpful information
            legal_moves = list(board.legal_moves)
            print(f"\nYou have {len(legal_moves)} legal moves.")
            
            # Show a few suggested moves
            if len(legal_moves) <= 8:
                print(f"Legal moves: {[str(move) for move in legal_moves]}")
            else:
                print(f"Some legal moves: {[str(move) for move in legal_moves[:8]]}...")
            
            # Prompt user for move
            move_input = input("\nEnter your move (e.g., 'e2e4') or 'quit'/'help': ").strip().lower()
            
            # Check if user wants to quit
            if move_input == 'quit':
                print("Thanks for playing!")
                exit()
            
            # Check if user wants help
            if move_input == 'help':
                print("\n=== QUICK HELP ===")
                print("• Enter moves in format: from_square + to_square (e.g., 'e2e4')")
                print("• Squares are named by file (a-h) and rank (1-8)")
                print("• For castling: 'e1g1' (kingside) or 'e1c1' (queenside)")
                print("• For promotion: add piece letter (e.g., 'e7e8q' for queen)")
                print("• Type 'quit' to exit the game")
                print("• Check 'how_to_play.txt' for detailed instructions\n")
                continue
            
            # Parse the move
            move = chess.Move.from_uci(move_input)
            
            # Check if the move is legal
            if move in board.legal_moves:
                return move
            else:
                print("❌ Illegal move! Please try again.")
                
                # Show why it might be illegal
                piece = board.piece_at(move.from_square)
                if piece is None:
                    print(f"No piece on {chess.square_name(move.from_square)}")
                elif piece.color != board.turn:
                    print(f"That's not your piece! (You are {'White' if board.turn else 'Black'})")
                else:
                    print("That move is not legal for that piece.")
                
        except ValueError:
            print("❌ Invalid move format! Please use UCI notation (e.g., 'e2e4').")
            print("Type 'help' for more information.")
        except Exception as e:
            print(f"❌ Error: {e}. Please try again.")


def main():
    """Main game loop for the chess engine."""
    
    print("=" * 60)
    print("🏆 WELCOME TO THE ENHANCED PYTHON CHESS ENGINE! 🏆")
    print("=" * 60)
    print("🔥 NEW FEATURES:")
    print("   • Stronger AI with advanced evaluation")
    print("   • Better move ordering and search algorithms")
    print("   • Improved tactical awareness")
    print("   • Enhanced king safety and pawn structure analysis")
    print("=" * 60)
    print("📖 You are playing as White, AI is playing as Black.")
    print("📝 Enter moves in UCI format (e.g., 'e2e4' for pawn from e2 to e4).")
    print("❓ Type 'help' for quick instructions or check 'how_to_play.txt'")
    print("🚪 Type 'quit' at any time to exit the game.")
    print("=" * 60)
    
    # Initialize the chess board
    board = chess.Board()
    
    # Set search depth for the AI (4-5 is stronger but slower)
    depth = 4
    move_count = 0
    
    # Game loop
    while not board.is_game_over():
        # Display current board position
        print_board_with_coordinates(board)
        
        if board.turn == chess.WHITE:
            # Human player's turn (White)
            print("Your turn (White):")
            move = get_user_move(board)
            board.push(move)
            print(f"✅ You played: {move}")
            move_count += 1
            
        else:
            # AI player's turn (Black)
            print("AI is thinking...")
            start_time = time.time()
            
            # Use iterative deepening for better performance in opening/endgame
            if move_count < 10 or len(board.piece_map()) < 10:
                # Use iterative deepening with time limit in opening/endgame
                ai_move = iterative_deepening_search(board, depth + 1, time_limit=5.0)
            else:
                # Use fixed depth search in middlegame
                ai_move = find_best_move(board, depth)
            
            think_time = time.time() - start_time
            
            if ai_move is None:
                print("AI couldn't find a move!")
                break
            
            # Make the AI's move
            board.push(ai_move)
            print(f"AI plays: {ai_move} (thought for {think_time:.1f}s)")
            move_count += 1
    
    # Game is over - display final position and result
    print_board_with_coordinates(board)
    
    # Determine and display the game result
    result = board.result()
    print("\n" + "=" * 50)
    print("🏁 GAME OVER! 🏁")
    print("=" * 50)
    
    if result == "1-0":
        print("🎉 CONGRATULATIONS! White (You) wins by checkmate!")
        print("🏆 You defeated the AI! Well played!")
    elif result == "0-1":
        print("💻 Black (AI) wins by checkmate!")
        print("🤖 The AI was stronger this time. Try again!")
    elif result == "1/2-1/2":
        if board.is_stalemate():
            print("🤝 Stalemate! The game is a draw.")
            print("⚖️ Neither side could achieve checkmate.")
        elif board.is_insufficient_material():
            print("🤝 Draw by insufficient material!")
            print("⚖️ Not enough pieces left to checkmate.")
        elif board.is_repetition():
            print("🤝 Draw by threefold repetition!")
            print("⚖️ The same position occurred three times.")
        else:
            print("🤝 The game is a draw.")
    
    print(f"\n📊 Final result: {result}")
    print(f"📈 Total moves played: {move_count}")
    print("\n🙏 Thanks for playing the Enhanced Chess Engine!")
    print("💡 Check 'how_to_play.txt' to improve your chess skills!")
    print("=" * 50)


if __name__ == "__main__":
    main()
