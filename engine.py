class GameState:
    def __init__(self):
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
        ]
        self.moveFunctions = {
            "p": self.getPawnMoves,
            "r": self.getRookMoves,
            "n": self.getKnightMoves,
            "b": self.getBishopMoves,
            "q": self.getQueenMoves,
            "k": self.getKingMoves,
        }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()
        self.currentCastlingRights = CastlingRights(True, True, True, True)
        self.castlingRightsLog = [
            CastlingRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs,
            )
        ]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove
        self.moveLog.append(move)
        if move.pieceMoved == "wk":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bk":
            self.blackKingLocation = (move.endRow, move.endCol)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "q"
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()
        if move.isCastlingMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1
                ]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2
                ]
                self.board[move.endRow][move.endCol - 2] = "--"
        self.updateCastlingRights(move)
        self.castlingRightsLog.append(
            CastlingRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs,
            )
        )

    def undoMove(self):
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wk":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bk":
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
            self.castlingRightsLog.pop()
            self.currentCastlingRights = self.castlingRightsLog[-1]
            if move.isCastlingMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1
                    ]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1
                    ]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkMate = False
            self.staleMate = False

    def updateCastlingRights(self, move):
        if move.pieceCaptured == "wr":
            if move.endCol == 0:
                self.currentCastlingRights.wqs = False
            elif move.endCol == 7:
                self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "br":
            if move.endCol == 0:
                self.currentCastlingRights.bqs = False
            elif move.endCol == 7:
                self.currentCastlingRights.bks = False

        if move.pieceMoved == "wk":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bk":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wr":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "br":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastlingRights = CastlingRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs,
        )
        moves = self.getPossibleMoves()
        if self.whiteToMove:
            self.getCastlingMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves
            )
        else:
            self.getCastlingMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves
            )
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRights = tempCastlingRights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enPassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True)
                    )
            if c + 1 < len(self.board[0]):
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enPassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True)
                    )
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enPassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True)
                    )
            if c + 1 < len(self.board[0]):
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enPassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True)
                    )

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        dim = len(self.board[0])
        for d in directions:
            for i in range(1, dim):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < dim and 0 <= endCol < dim:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        allyColor = "w" if self.whiteToMove else "b"
        dim = len(self.board[0])
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < dim and 0 <= endCol < dim:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        dim = len(self.board[0])
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < dim and 0 <= endCol < dim:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = (
            (-1, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
        )
        allyColor = "w" if self.whiteToMove else "b"
        dim = len(self.board[0])
        for i in range(dim):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < dim and 0 <= endCol < dim:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastlingMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
            not self.whiteToMove and self.currentCastlingRights.bks
        ):
            self.getKingCastlingMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
            not self.whiteToMove and self.currentCastlingRights.bqs
        ):
            self.getQueenCastlingMoves(r, c, moves)

    def getKingCastlingMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(
                r, c + 2
            ):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastlingMove=True))

    def getQueenCastlingMoves(self, r, c, moves):
        if (
            self.board[r][c - 1] == "--"
            and self.board[r][c - 2] == "--"
            and self.board[r][c - 3] == "--"
        ):
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(
                r, c - 2
            ):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastlingMove=True))


class CastlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(
        self, startSq, endSq, board, isEnPassantMove=False, isCastlingMove=False
    ):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
            self.pieceMoved == "bp" and self.endRow == 7
        )
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCastlingMove = isCastlingMove

        self.moveId = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
