############################################################################################################################################################################################
# Name: Devon Knudsen
# Student #: 10260170
# Date: 11/16/2020
# Assignment #3 - An Intelligent Othello Player: A program that plays the game othello in both human vs human mode as well as human vs AI mode.
#                                                The AI is driven by a mini-max heuristic search algorithm that prioritizes corner posession and limiting the human player's piece mobility.
#############################################################################################################################################################################################

from collections import deque
from copy import deepcopy

AMOUNT_BLACK_PIECES = 30
BLACK_PIECE = "B"
AMOUNT_WHITE_PIECES = 30
WHITE_PIECE = "W"
SEARCH_DEPTH = 6
INF = 999999999999999
DISPLAY_SEQUENCES = False
DISPLAY_AVAILABLE_MOVES = False
ALPHA_BETA_PRUNING = False

# function that displays the main menu
# calls the select mode menu
def mainMenu():
    print("[1] Play Othello\n" + 
          "[0] Exit")
    choice = input("Enter choice: ")
    if(choice == "1"):
        selectMode()
    elif(choice == "0"):
        exit(0)
    else:
        mainMenu()

# select mode menu
# begins the game vs another player or against the AI depending on what the player chooses 
def selectMode():
    print("[1] Vs Human\n" +
          "[2] Vs AI\n" +
          "[3] Go Back")
    choice = input("Enter choice: ")
    if(choice == "1"):
        vsPlayer()
    elif(choice == "2"):
        vsAI()
    elif(choice == "3"):
        mainMenu()
    else:
        selectMode()

# begins the game in human vs human mode
def vsPlayer():

    # set first player to black and create board
    currPlayer = "Black"
    currBoard = createBoard()

    # play game until the endgame state is reached
    while(True):
        printBoard(currBoard)
        printPiecesLeft(currPlayer)
        potentialMoves = availableMoves(currPlayer, currBoard)

        # if the current player cannot make a move, their turn is skipped
        if(len(potentialMoves) == 0):
            print("<{}'s> turn skipped. They cannot outflank any opposing disk".format(currPlayer))
            currPlayer = switchPlayers(currPlayer)
            continue

        if(DISPLAY_AVAILABLE_MOVES):
            print("Available moves:", potentialMoves)
        
        # ask current player to enter coordinate
        currMove = input("<{}>, enter coordinate: ".format(currPlayer)).upper()
        currBoard = modifyBoard(currBoard, currMove, currPlayer, potentialMoves)
        currPlayer = switchPlayers(currPlayer)

        # if end state is reached
        if(endGame(currBoard, AMOUNT_BLACK_PIECES, AMOUNT_WHITE_PIECES) == True):
            break
    
    printBoard(currBoard)
    winner = declareWinner(currBoard)
    print("<{}> is the winner!".format(winner))
    
# begins the game in human vs AI mode
def vsAI():
    global DISPLAY_SEQUENCES, ALPHA_BETA_PRUNING

    # create game board and ask human if they would like to be the first player
    currBoard = createBoard()
    choice = input("Would you like to be first player? ").upper()

    # if not, the AI makes its first move
    if(choice == "NO" or choice == "N"):

        # ask if the human would like minimax's move sequences to be displayed
        askToDisplay = input("Would you like to display sequences of moves considered by AI on its next turn? ").upper()
        if(askToDisplay == "Y" or askToDisplay == "YES"):
            DISPLAY_SEQUENCES = True
        elif(askToDisplay == "N" or askToDisplay == "NO"):
            DISPLAY_SEQUENCES = False

        # ask if the human would like the AI to use alpha beta pruning this turn
        askForAlphaBetaPruning = input("Would you like to enable the use of alpha-beta pruning on the AI's next turn? ").upper()
        if(askForAlphaBetaPruning == "Y" or askForAlphaBetaPruning == "YES"):
            ALPHA_BETA_PRUNING = True
        elif(askForAlphaBetaPruning == "N" or askForAlphaBetaPruning == "NO"):
            ALPHA_BETA_PRUNING = False

        # set human to player two and AI to player one
        humanColor = "White"
        AIColor = "Black"

        printBoard(currBoard)
        printPiecesLeft(AIColor)
        potentialMoves = availableMoves(AIColor, currBoard)

        if(DISPLAY_AVAILABLE_MOVES):
            print("Available moves:", potentialMoves)

        # AI chooses move and displays it
        currMove = AIChooseMove(currBoard, AIColor, humanColor)
        print("MOVE MADE:", currMove)
        currBoard = modifyBoard(currBoard, currMove, AIColor, potentialMoves)
        
        reducePieceCount(AIColor)

    elif(choice == "YES" or choice == "Y"):
        # set human to player one and AI to player two
        humanColor = "Black"
        AIColor = "White"
    
    # human starts as the current player before entering the gameplay loop
    currPlayer = humanColor
    while(True):
        printBoard(currBoard)
        printPiecesLeft(currPlayer)
        potentialMoves = availableMoves(currPlayer, currBoard)

        # if the current player cannot make a move, their turn is skipped
        if(len(potentialMoves) == 0):
            print("<{}'s> turn skipped. They cannot outflank any opposing disk".format(currPlayer))
            currPlayer = switchPlayers(currPlayer)
            continue
        
        if(DISPLAY_AVAILABLE_MOVES):
            print("Available moves:", potentialMoves)
        
        if(currPlayer == humanColor):
            currMove = input("<{}>, enter coordinate: ".format(currPlayer)).upper()

            askToDisplay = input("Would you like to display sequences of moves considered by AI on its next turn? ").upper()
            if(askToDisplay == "Y" or askToDisplay == "YES"):
                DISPLAY_SEQUENCES = True
            elif(askToDisplay == "N" or askToDisplay == "NO"):
                DISPLAY_SEQUENCES = False

            askForAlphaBetaPruning = input("Would you like to enable the use of alpha-beta pruning on the AI's next turn? ").upper()
            if(askForAlphaBetaPruning == "Y" or askForAlphaBetaPruning == "YES"):
                ALPHA_BETA_PRUNING = True
            elif(askForAlphaBetaPruning == "N" or askForAlphaBetaPruning == "NO"):
                ALPHA_BETA_PRUNING = False
        else:
            currMove = AIChooseMove(currBoard, AIColor, humanColor)
            print("MOVE MADE:", currMove)

        currBoard = modifyBoard(currBoard, currMove, currPlayer, potentialMoves)
        reducePieceCount(currPlayer)
        currPlayer = switchPlayers(currPlayer)
        if(endGame(currBoard, AMOUNT_BLACK_PIECES, AMOUNT_WHITE_PIECES) == True):
            break
    
    printBoard(currBoard)
    winner = declareWinner(currBoard)
    print("<{}> is the winner!".format(winner))

# create the initial game board
def createBoard():
    blankBoard = [["", "A", "B", "C", "D", "E", "F", "G", "H"]]

    for i in range(8):
        blankBoard.append([i + 1, "-", "-", "-", "-", "-", "-", "-", "-"])
    
    blankBoard[4][4] = WHITE_PIECE
    blankBoard[4][5] = BLACK_PIECE
    blankBoard[5][4] = BLACK_PIECE
    blankBoard[5][5] = WHITE_PIECE
    
    return blankBoard

# copies the game board as it currently is
# used in the minimax function so a copy of the board can be made so the real board isn't mutated
def copyBoard(board):
    newBoard = [[-1 for n in range(len(board))] for m in range(len(board))]
    for i in range(len(board)):
        for j in range(len(board[i])):
            newBoard[i][j] = board[i][j]
    
    return newBoard

def printBoard(currBoard):
    for row in currBoard:
        print(row)

# prints the amount of pieces left for each player during their turn
def printPiecesLeft(player):
    global AMOUNT_BLACK_PIECES, AMOUNT_WHITE_PIECES
    if(player == "Black"):
        print("Pieces Left:", AMOUNT_BLACK_PIECES)
    else:
        print("Pieces Left:", AMOUNT_WHITE_PIECES)

# finds all available moves for all current player's pieces on the board
# returns all potential moves
def availableMoves(player, board):
    global BLACK_PIECE, WHITE_PIECE
    potentialMoves = []

    # set what piece type to search for
    if(player == "Black"):
        searchingFor = BLACK_PIECE
        lookingToOutflank = WHITE_PIECE
    else:
        searchingFor = WHITE_PIECE
        lookingToOutflank = BLACK_PIECE
    
    # iterate through the game board
    for i in range(1, len(board)):
        for j in range(1, len(board[i])):

            # if you found a piece type you're searching for, check potential moves in all directions
            if(board[i][j] == searchingFor):

                # call all functions to check for potential moves
                moveUp = lookUp(i, j, searchingFor, lookingToOutflank, board)
                moveTopRight = lookTopRight(i, j, searchingFor, lookingToOutflank, board)
                moveRight = lookRight(i, j, searchingFor, lookingToOutflank, board)
                moveBottomRight = lookBottomRight(i, j, searchingFor, lookingToOutflank, board)
                moveDown = lookDown(i, j, searchingFor, lookingToOutflank, board)
                moveBottomLeft = lookBottomLeft(i, j, searchingFor, lookingToOutflank, board)
                moveLeft = lookLeft(i, j, searchingFor, lookingToOutflank, board)
                moveTopLeft = lookTopLeft(i, j, searchingFor, lookingToOutflank, board)
                
                # append potential moves to array to be returned
                if(moveUp != -1):
                    moveUpResults = indexToCoordinate(moveUp)
                    if(moveUpResults not in potentialMoves):
                        potentialMoves.append(moveUpResults)
                if(moveTopRight != -1):
                    moveTopRightResults = indexToCoordinate(moveTopRight)
                    if(moveTopRightResults not in potentialMoves):
                        potentialMoves.append(moveTopRightResults)
                if(moveRight != -1):
                    moveRightResults = indexToCoordinate(moveRight)
                    if(moveRightResults not in potentialMoves):
                        potentialMoves.append(moveRightResults)
                if(moveBottomRight != -1):
                    moveBottomRightResults = indexToCoordinate(moveBottomRight)
                    if(moveBottomRightResults not in potentialMoves):
                        potentialMoves.append(moveBottomRightResults)
                if(moveDown != -1):
                    moveDownResults = indexToCoordinate(moveDown)
                    if(moveDownResults not in potentialMoves):
                        potentialMoves.append(moveDownResults)
                if(moveBottomLeft != -1):
                    moveBottomLeftResults = indexToCoordinate(moveBottomLeft)
                    if(moveBottomLeftResults not in potentialMoves):
                        potentialMoves.append(moveBottomLeftResults)
                if(moveLeft != -1):
                    moveLeftResults = indexToCoordinate(moveLeft)
                    if(moveLeftResults not in potentialMoves):
                        potentialMoves.append(moveLeftResults)
                if(moveTopLeft != -1):
                    moveTopLeftResults = indexToCoordinate(moveTopLeft)
                    if(moveTopLeftResults not in potentialMoves):
                        potentialMoves.append(moveTopLeftResults)

    return potentialMoves

# checks if current player can make a legal move going up with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position                
def lookUp(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):

        # check to see if you're attempting to look off an edge of the board
        if(rowPosition - 1 < 1):
            return -1

        # place the array positions of the opposite players pieces into stack
        if(board[rowPosition - 1][columnPosition] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition - 1][columnPosition])
            rowPosition -= 1
            if(rowPosition < 1):
                return -1
        
        # if the current array position indicates an empty space on the board, return its position within the array
        elif(board[rowPosition - 1][columnPosition] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition - 1, columnPosition)
        else:
            return -1

# checks if current player can make a legal move going down with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookDown(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(rowPosition + 1 > len(board) - 1):
            return -1

        if(board[rowPosition + 1][columnPosition] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition + 1][columnPosition])
            rowPosition += 1
            if(rowPosition > len(board) - 1):
                return -1
        elif(board[rowPosition + 1][columnPosition] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition + 1, columnPosition)
        else:
            return -1

# checks if current player can make a legal move going right with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(columnPosition + 1 > len(board[rowPosition]) - 1):
            return -1

        if(board[rowPosition][columnPosition + 1] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition][columnPosition + 1])
            columnPosition += 1
            if(columnPosition > len(board[rowPosition]) - 1):
                return -1
        elif(board[rowPosition][columnPosition + 1] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition, columnPosition + 1)
        else:
            return -1

# checks if current player can make a legal move going left with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(columnPosition - 1 < 1):
            return -1

        if(board[rowPosition][columnPosition - 1] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition][columnPosition - 1])
            columnPosition -= 1
            if(columnPosition < 1):
                return -1
        elif(board[rowPosition][columnPosition - 1] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition, columnPosition - 1)
        else:
            return -1

# checks if current player can make a legal move going up right with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookTopRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(rowPosition - 1 < 1 or columnPosition + 1 > len(board[rowPosition]) - 1):
            return -1

        if(board[rowPosition - 1][columnPosition + 1] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition - 1][columnPosition + 1])
            rowPosition -= 1
            columnPosition += 1
            if(rowPosition < 1 or columnPosition > len(board[rowPosition]) - 1):
                return -1
        elif(board[rowPosition - 1][columnPosition + 1] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition - 1, columnPosition + 1)
        else:
            return -1

# checks if current player can make a legal move going down right with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookBottomRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(rowPosition + 1 > len(board) - 1 or columnPosition + 1 > len(board[rowPosition]) - 1):
            return -1

        if(board[rowPosition + 1][columnPosition + 1] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition + 1][columnPosition + 1])
            rowPosition += 1
            columnPosition += 1
            if(rowPosition > len(board) - 1 or columnPosition > len(board[rowPosition]) - 1):
                return -1
        elif(board[rowPosition + 1][columnPosition + 1] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition + 1, columnPosition + 1)
        else:
            return -1

# checks if current player can make a legal move going up left with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookTopLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(rowPosition - 1 < 1 or columnPosition - 1 < 1):
            return -1

        if(board[rowPosition - 1][columnPosition - 1] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition - 1][columnPosition - 1])
            rowPosition -= 1
            columnPosition -= 1
            if(rowPosition < 1 or columnPosition < 1):
                break
        elif(board[rowPosition - 1][columnPosition - 1] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition - 1, columnPosition - 1)
        else:
            return -1

# checks if current player can make a legal move going down left with current player's piece on the board
# returns the position if a legal move is possible in the current player's current piece position
# returns -1 if you cannot make a legal move from the current position
def lookBottomLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    pieceStack = deque()
    pieceStack.append(playerPiece)
    while(True):
        if(rowPosition + 1 > len(board) - 1 or columnPosition - 1 < 1):
            return -1

        if(board[rowPosition + 1][columnPosition - 1] == oppositePlayerPiece):
            pieceStack.append(board[rowPosition + 1][columnPosition - 1])
            rowPosition += 1
            columnPosition -= 1
            if(rowPosition > len(board) - 1 or columnPosition < 1):
                break
        elif(board[rowPosition + 1][columnPosition - 1] == "-"):
            poppedPiece = pieceStack.pop()
            if(poppedPiece == playerPiece):
                return -1
            elif(poppedPiece == oppositePlayerPiece):
                return (rowPosition + 1, columnPosition - 1)
        else:
            return -1

# returns the next version of the board after all other pieces are outflanked due to piece placement
def modifyBoard(board, move, player, availableMoves):
    
    # check if the input move is within the moves that can be made by the current player
    moveInList = False
    for i in range(len(availableMoves)):
        if(availableMoves[i] == move):
            moveInList = True
    
    # if an illegal move is input, it is rejected
    if(moveInList != True):
        retry = input("[MOVE REJECTED] That is an illegal move. Please enter a legal move: ").upper()
        modifyBoard(board, retry, player, availableMoves)
    
    # place piece and check if you can outflank in all directions
    else:
        row, column = coordinateToIndex(move)
        if(player == "Black"):
            playerPiece = BLACK_PIECE
            oppositePlayerPiece = WHITE_PIECE
        else:
            playerPiece = WHITE_PIECE
            oppositePlayerPiece = BLACK_PIECE
        board[row][column] = playerPiece
        modBoard = outflankAllDirections(row, column, playerPiece, oppositePlayerPiece, board)
    
    return board

# reduces the piece count of the current player after a piece location is decided
def reducePieceCount(playerColor):
    global AMOUNT_BLACK_PIECES, AMOUNT_WHITE_PIECES
    if(playerColor == "Black"):
        
        # if a player runs out of disks, the opponent must give the player their disk
        if(AMOUNT_BLACK_PIECES == 0 and AMOUNT_WHITE_PIECES != 0):
            AMOUNT_WHITE_PIECES -= 1
        else:
            AMOUNT_BLACK_PIECES -= 1
    else:
        if(AMOUNT_WHITE_PIECES == 0 and AMOUNT_BLACK_PIECES != 0):
            AMOUNT_BLACK_PIECES -= 1
        else:
            AMOUNT_WHITE_PIECES -= 1

# calls to all outflank functions
# modifies the passed in board if a given outflank direction's function returns a board change
# returns the fully modified board with all outflanks accounted for
def outflankAllDirections(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    flipUp = outflankUp(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipUp != -1):
        board = flipUp

    flipDown = outflankDown(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipDown != -1):
        board = flipDown

    flipRight = outflankRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipRight != -1):
        board = flipRight
    
    flipLeft = outflankLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipLeft != -1):
        board = flipLeft

    flipDownLeft = outflankDownLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipDownLeft != -1):
        board = flipDownLeft

    flipDownRight = outflankDownRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipDownRight != -1):
        board = flipDownRight

    flipUpLeft = outflankUpLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipUpLeft != -1):
        board = flipUpLeft

    flipUpRight = outflankUpRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board)
    if(flipUpRight != -1):
        board = flipUpRight
    
    return board

# flips pieces going upward if piece if placed below opponent piece
def outflankUp(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    
    # check to see if you're attempting to flip at an edge of the board
    rowPosition -= 1
    if(rowPosition < 1):
        return -1

    # place the array positions of the opposite players pieces into stack
    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        rowPosition -= 1
        if(rowPosition < 1):
            return -1

    # if the position after the last opposite player's piece is not the current player's piece, return -1 to indicate that you cannot outflank 
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1
    
    # outflank moving upward
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going downward if piece is placed above opponent piece
def outflankDown(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    rowPosition += 1
    if(rowPosition > len(board) - 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        rowPosition += 1
        if(rowPosition > len(board) - 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going right if piece is placed left of opponent piece
def outflankRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    columnPosition += 1
    if(columnPosition > len(board[rowPosition]) - 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        columnPosition += 1
        if(columnPosition > len(board[rowPosition]) - 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going left if piece is placed right of opponent piece
def outflankLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    columnPosition -= 1
    if(columnPosition < 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        columnPosition -= 1
        if(columnPosition < 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going down left if piece is placed top right of opponent piece
def outflankDownLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    rowPosition += 1
    columnPosition -= 1
    if(rowPosition > len(board) - 1 or columnPosition < 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        rowPosition += 1
        columnPosition -= 1
        if(rowPosition > len(board) - 1 or columnPosition < 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going down right if piece is placed top left of opponent piece
def outflankDownRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    rowPosition += 1
    columnPosition += 1
    if(rowPosition > len(board) - 1 or columnPosition > len(board[rowPosition]) - 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        rowPosition += 1
        columnPosition += 1
        if(rowPosition > len(board) - 1 or columnPosition > len(board[rowPosition]) - 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going up left if piece is placed bottom right of opponent piece
def outflankUpLeft(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    rowPosition -= 1
    columnPosition -= 1
    if(rowPosition < 1 or columnPosition < 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        rowPosition -= 1
        columnPosition -= 1
        if(rowPosition < 1 or columnPosition < 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# flips pieces going up right if piece is placed bottom left of opponent piece
def outflankUpRight(rowPosition, columnPosition, playerPiece, oppositePlayerPiece, board):
    piecePositionStack = deque()
    rowPosition -= 1
    columnPosition += 1
    if(rowPosition < 1 or columnPosition > len(board[rowPosition]) - 1):
        return -1

    while(board[rowPosition][columnPosition] == oppositePlayerPiece):
        piecePositionStack.append((rowPosition, columnPosition))
        rowPosition -= 1
        columnPosition += 1
        if(rowPosition < 1 or columnPosition > len(board[rowPosition]) - 1):
            return -1
    
    if(board[rowPosition][columnPosition] == "-" or len(piecePositionStack) == 0):
        return -1    
    elif(board[rowPosition][columnPosition] == playerPiece):
            while(len(piecePositionStack) > 0):
                poppedPiecePosition = piecePositionStack.pop()
                board[poppedPiecePosition[0]][poppedPiecePosition[1]] = playerPiece
    
    return board

# converts a tuple of game board coordinates to their 2D array indecies equivalents
# used in the modify board function to place a player's piece in its desired location
def coordinateToIndex(inputCoordinate):
    letterToColumnIndex = {"A": 1,
                           "B": 2,
                           "C": 3,
                           "D": 4,
                           "E": 5,
                           "F": 6,
                           "G": 7,
                           "H": 8}
    column = letterToColumnIndex[inputCoordinate[0].upper()]
    row = int(inputCoordinate[1])    
    
    return row, column

# converts a tuple of indecies from the 2D array into their game board equivalents
# used in the available moves function to convert potential indecies to place a piece to printable coordinates
def indexToCoordinate(indexTuple):
    letterToColumnIndex = {1: "A",
                           2: "B",
                           3: "C",
                           4: "D",
                           5: "E",
                           6: "F",
                           7: "G",
                           8: "H"}
    column = letterToColumnIndex[indexTuple[1]].upper()
    row = str(indexTuple[0])    
    
    coordinate = column + row
    
    return coordinate

# switches players
def switchPlayers(player):
    if(player == "Black"):
        return "White"
    else:
        return "Black"

# returns the move chosen by the minimax algorithm
def AIChooseMove(board, AIColor, humanColor):

    # create a copy of the piece counts for both players
    # done to not mutate the real piece counts while AI is figuring out its move choice
    AIPieceCount = 0
    humanPieceCount = 0
    if(AIColor == "Black"):
        AIPieceCount = AMOUNT_BLACK_PIECES
        humanPieceCount = AMOUNT_WHITE_PIECES
    else:
        AIPieceCount = AMOUNT_WHITE_PIECES
        humanPieceCount = AMOUNT_BLACK_PIECES

    cost, moveChoosen, states = miniMax(SEARCH_DEPTH, True, board, -INF, INF, AIColor, humanColor, 0, deque(), None, AIPieceCount, humanPieceCount)
    print("STATES EXAMINED BEFORE MAKING MOVE:", states)

    return moveChoosen

# full implementation of the minimax algorithm with alpha-beta pruning
# returns the maxmized cost for the AI, the move associated with getting there and the number of states that were examined
def miniMax(depth, maxingPlayer, board, alpha, beta, AIColor, humanColor, numStatesExamined, sequence, move, AIPieceCount, humanPieceCount):

    # if at the desired depth or in a game over state, return static evaluation of current node
    if(depth == 0 or endGame(board, AIPieceCount, humanPieceCount)):
        
        heuristicValue = staticEvaluation(board, AIColor, humanColor, move, AIPieceCount, humanPieceCount)
        if DISPLAY_SEQUENCES:

            # reverse the sequence stack for printing
            sequenceReverse = deepcopy(sequence)
            sequenceReverse.reverse()

            while(len(sequenceReverse) != 0):
                move = sequenceReverse.pop()
                if(len(sequenceReverse) >= 1):
                    print(move, "-> ", end =" ")
                else:
                    print(move, "HEURISTIC VALUE:", heuristicValue)

        return heuristicValue, None, numStatesExamined
    
    if(maxingPlayer == True):
        maximumEval = -INF
        potentialMoves = availableMoves(AIColor, board)
        for move in potentialMoves:

            # copy the current board before making next move
            # to not mutate the original passed in board
            modBoard = copyBoard(board)
            modBoard = modifyBoard(modBoard, move, AIColor, potentialMoves)

            # push move and color tuple to the sequence stack for printing
            sequence.append((AIColor, move))

            # decrement the piece count, for the purpose of determining whether 
            # or not the game will be over in a given position before making placement choice
            AIPieceCount -= 1

            # descend one level and allow minimizing player to make move
            eval, nextMove, numStatesExamined = miniMax(depth - 1, False, modBoard, alpha, beta, AIColor, humanColor, numStatesExamined + 1, sequence, move, AIPieceCount, humanPieceCount)
            maximumEval = max(maximumEval, eval)

            sequence.pop()
            AIPieceCount += 1

            if(ALPHA_BETA_PRUNING == True):
                alpha = max(alpha, maximumEval)
                if beta <= alpha:
                    break

        return maximumEval, move, numStatesExamined
    
    else:
        minimumEval = INF
        potentialMoves = availableMoves(humanColor, board)
        for move in potentialMoves:

            # copy the current board before making next move
            # to not mutate the original passed in board
            modBoard = copyBoard(board)
            modBoard = modifyBoard(modBoard, move, humanColor, potentialMoves)

            sequence.append((humanColor, move))
            humanPieceCount -= 1

            # descend one level and allow maximizing player to make move
            eval, nextMove, numStatesExamined = miniMax(depth - 1, True, modBoard, alpha, beta, AIColor, humanColor, numStatesExamined + 1, sequence, move, AIPieceCount, humanPieceCount)
            minimumEval = min(minimumEval, eval)

            sequence.pop()
            humanPieceCount += 1
            
            if(ALPHA_BETA_PRUNING == True):
                beta = min(beta, minimumEval)
                if beta <= alpha:
                    break

        return minimumEval, move, numStatesExamined

# current heuristic is 2 part: 
# 1) if no corners taken, prioritize slowing the human player's amount of moves (mobility)
#       + values indicate the human player has less moves to make than the AI
#       - values indicate the human player has more moves to make than the AI
# 2) if corners are taken, prioritize taking corners while also slowing human player's mobility
#       + values indicate the AI has taken more corners than the human and/or the human player has less moves to make than the AI
#       + values indicate the AI has taken less corners than the human and/or the human player has more moves to make than the AI
# returns +/- 100 if the move would cause one of the players to win
def staticEvaluation(board, AIColor, humanColor, move, AIPieceCount, humanPieceCount):
    evaluation = 0
    if(AIColor == "Black"):
        AICornersCaptured, humanCornersCaptured = countCorners(board)
    else:
        humanCornersCaptured, AICornersCaptured = countCorners(board)

    if(endGame(board, AIPieceCount, humanPieceCount)):
        winner = declareWinner(board)
        if(winner == AIColor):
            evaluation = 100
        else:
            evaluation = -100

        return evaluation
        
    elif(AICornersCaptured + humanCornersCaptured != 0):
        cornerPriority = 20 * (AICornersCaptured - humanCornersCaptured)/(AICornersCaptured + humanCornersCaptured)
        AIMovesLeft = len(availableMoves(AIColor, board))
        humanMovesLeft = len(availableMoves(humanColor, board))
        mobilityValue = 80 * (AIMovesLeft - humanMovesLeft)/(AIMovesLeft + humanMovesLeft)
        
        evaluation += cornerPriority + mobilityValue
        
        return evaluation
        
    AIMovesLeft = len(availableMoves(AIColor, board))
    humanMovesLeft = len(availableMoves(humanColor, board))
    mobilityValue = 100 * (AIMovesLeft - humanMovesLeft)/(AIMovesLeft + humanMovesLeft)
    evaluation += mobilityValue

    return evaluation

# counts up which player has taken which corners of the board in its current state
# used in the static evaluation function
def countCorners(board):
    blackCorners = 0
    whiteCorners = 0
    if(board[1][1] == "B"):
        blackCorners += 1
    elif(board[1][1] == "W"):
        whiteCorners += 1
    if(board[1][8] == "B"):
        blackCorners += 1
    elif(board[1][8] == "W"):
        whiteCorners += 1
    if(board[8][1] == "B"):
        blackCorners += 1
    elif(board[8][1] == "W"):
        whiteCorners += 1
    if(board[8][8] == "B"):
        blackCorners += 1
    elif(board[8][8] == "W"):
        whiteCorners += 1
    
    return blackCorners, whiteCorners

# checks if the game is in a complete state: both players have no pieces or neither have any moves left
# returns true if in end game state
# returns false if not
def endGame(board, player1PieceCount, player2PieceCount):
    global AMOUNT_BLACK_PIECES, AMOUNT_WHITE_PIECES
    blackMovesLeft = len(availableMoves("Black", board))
    whiteMovesLeft = len(availableMoves("White", board))
    if(player1PieceCount + player2PieceCount == 0):
        return True
    elif(blackMovesLeft == 0 and whiteMovesLeft == 0):
        return True
    else:
        return False

# counts the amount of each players pieces on the board
# player with the most pieces on the board wins
def declareWinner(board):
    blackPieceCount = 0
    whitePieceCount = 0
    for i in range(1, len(board)):
        for j in range(1, len(board[i])):
            if(board[i][j] == "B"):
                blackPieceCount += 1
            elif(board[i][j] == "W"):
                whitePieceCount += 1
            else:
                continue
    if(blackPieceCount > whitePieceCount):
        return "Black"
    elif(whitePieceCount > blackPieceCount):
        return "White"

if __name__ == "__main__":
    while(True):
        mainMenu()