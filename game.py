from abc import ABC, abstractmethod
from datetime import datetime
import random


class Base(ABC):
    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def key(self):
        pass

    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()

    def __lt__(self, other):
        return self.key() < other.key()

    def __gt__(self, other):
        return self.key() > other.key()

    def __le__(self, other):
        return self.key() <= other.key()

    def __ge__(self, other):
        return self.key() >= other.key()

    def __hash__(self):
        return hash(self.key())

    def __repr__(self):
        return f"{self.__class__.__name__}{self.key()}"

    def __str__(self):
        return self.info()


class Pair(Base):
    def __init__(self, k, v):
        self._k = k
        self._v = v

    def get_k(self):
        return self._k

    def set_k(self, k):
        self._k = k

    def get_v(self):
        return self._v

    def set_v(self, v):
        self._v = v

    def info(self):
        return f"{self._k}: {self._v}"

    def key(self):
        return (self._k,)

    def __iter__(self):
        yield self._k
        yield self._v

    def __getitem__(self, i):
        return (self._k, self._v)[i]

    def __bool__(self):
        return self._v is not None


class MyMap(Base):
    def __init__(self):
        self._items = []

    def get_items(self):
        return self._items

    def set_items(self, items):
        self._items = list(items)

    def info(self):
        return "MyMap из %d пар" % len(self._items)

    def key(self):
        return tuple(self.items())

    def find(self, k):
        for p in self._items:
            if p.get_k() == k:
                return p
        return None

    def get(self, k, default=None):
        p = self.find(k)
        return default if p is None else p.get_v()

    def items(self):
        return [(p.get_k(), p.get_v()) for p in self._items]

    def __setitem__(self, k, v):
        p = self.find(k)
        if p is None:
            self._items.append(Pair(k, v))
        else:
            p.set_v(v)

    def __getitem__(self, k):
        p = self.find(k)
        if p is None:
            raise KeyError(k)
        return p.get_v()

    def __contains__(self, k):
        return self.find(k) is not None

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(p.get_k() for p in self._items)

    def __str__(self):
        return ", ".join(str(p) for p in self._items)


class Cell(Base):
    def __init__(self, row, col):
        self._row = row
        self._col = col
        self._mark = ""

    def get_row(self):
        return self._row

    def set_row(self, row):
        self._row = row

    def get_col(self):
        return self._col

    def set_col(self, col):
        self._col = col

    def get_mark(self):
        return self._mark

    def set_mark(self, mark):
        if mark not in ("", "X", "O"):
            raise ValueError("bad mark")
        self._mark = mark

    def index(self):
        return self._row * 3 + self._col

    def empty(self):
        return self._mark == ""

    def info(self):
        return f"[{self._row},{self._col}] {self._mark or '-'}"

    def key(self):
        return (self._row, self._col)

    def __bool__(self):
        return not self.empty()

    def __int__(self):
        return self.index()

    def __contains__(self, mark):
        return self._mark == mark


class Player(Base):
    def __init__(self, name, mark):
        self._name = name
        self._mark = mark
        self._wins = 0

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_mark(self):
        return self._mark

    def set_mark(self, mark):
        self._mark = mark

    def get_wins(self):
        return self._wins

    def set_wins(self, wins):
        self._wins = wins

    def win(self):
        self._wins += 1

    def info(self):
        return f"{self._name} ({self._mark}) - {self._wins}"

    def key(self):
        return (self._wins, self._name)

    def __call__(self):
        return self._mark

    def __int__(self):
        return self._wins

    def __iadd__(self, n):
        self._wins += n
        return self


class Board(Base):
    LINES = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))

    def __init__(self):
        self._cells = tuple(Cell(r, c) for r in range(3) for c in range(3))

    def get_cells(self):
        return self._cells

    def set_cells(self, cells):
        self._cells = tuple(cells)

    def reset(self):
        for c in self._cells:
            c.set_mark("")

    def free(self):
        return [c for c in self._cells if c.empty()]

    def full(self):
        return len(self.free()) == 0

    def win_line(self):
        for a, b, c in self.LINES:
            m = self._cells[a].get_mark()
            if m and m == self._cells[b].get_mark() == self._cells[c].get_mark():
                return (a, b, c)
        return ()

    def winner(self):
        line = self.win_line()
        return self._cells[line[0]].get_mark() if line else ""

    def info(self):
        rows = []
        for r in range(3):
            rows.append(" ".join(self._cells[r * 3 + c].get_mark() or "." for c in range(3)))
        return "\n".join(rows)

    def key(self):
        return tuple(c.get_mark() for c in self._cells)

    def __len__(self):
        return sum(1 for c in self._cells if c)

    def __getitem__(self, i):
        return self._cells[i]

    def __iter__(self):
        return iter(self._cells)

    def __contains__(self, cell):
        return cell in self._cells


class Game(Base):
    def __init__(self, human, computer, level="Нормально"):
        self._board = Board()
        self._human = human
        self._computer = computer
        self._level = level
        self._over = False
        self._result = ""

    def get_board(self):
        return self._board

    def set_board(self, board):
        self._board = board

    def get_human(self):
        return self._human

    def set_human(self, player):
        self._human = player

    def get_computer(self):
        return self._computer

    def set_computer(self, player):
        self._computer = player

    def get_level(self):
        return self._level

    def set_level(self, level):
        self._level = level

    def is_over(self):
        return self._over

    def get_result(self):
        return self._result

    def restart(self):
        self._board.reset()
        self._over = False
        self._result = ""

    def move(self, i):
        cell = self._board[i]
        if self._over or not cell.empty():
            return False
        cell.set_mark(self._human())
        self.check()
        if not self._over:
            target = Game.pick(self._board, self._computer(), self._human(), self._level)
            target.set_mark(self._computer())
            self.check()
        return True

    def check(self):
        w = self._board.winner()
        if w == self._human():
            self._over = True
            self._result = "win"
            self._human.win()
        elif w == self._computer():
            self._over = True
            self._result = "lose"
            self._computer.win()
        elif self._board.full():
            self._over = True
            self._result = "draw"

    def info(self):
        return f"Игра {self._human.get_name()} vs {self._computer.get_name()}, {self._level}"

    def key(self):
        return (self._human.get_name(), self._level)

    def __call__(self, i):
        return self.move(i)

    def __bool__(self):
        return not self._over

    def __len__(self):
        return len(self._board)

    @staticmethod
    def pick(board, me, enemy, level):
        free = board.free()
        if level == "Легко":
            return random.choice(free)
        if level == "Сложно":
            best = None
            best_score = -2
            for c in free:
                c.set_mark(me)
                s = Game.minimax(board, me, enemy, False)
                c.set_mark("")
                if s > best_score:
                    best_score = s
                    best = c
            return best
        for mark in (me, enemy):
            for c in free:
                c.set_mark(mark)
                ok = board.winner() == mark
                c.set_mark("")
                if ok:
                    return c
        if board[4].empty():
            return board[4]
        return random.choice(free)

    @staticmethod
    def minimax(board, me, enemy, my_turn):
        w = board.winner()
        if w == me:
            return 1
        if w == enemy:
            return -1
        if board.full():
            return 0
        scores = []
        for c in board.free():
            c.set_mark(me if my_turn else enemy)
            scores.append(Game.minimax(board, me, enemy, not my_turn))
            c.set_mark("")
        return max(scores) if my_turn else min(scores)


class Session(Base):
    FMT = "%d.%m.%Y %H:%M:%S"

    def __init__(self, login):
        self._login = login
        self._time_in = datetime.now()
        self._time_out = None

    def get_login(self):
        return self._login

    def set_login(self, login):
        self._login = login

    def get_time_in(self):
        return self._time_in

    def set_time_in(self, t):
        self._time_in = t

    def get_time_out(self):
        return self._time_out

    def set_time_out(self, t):
        self._time_out = t

    def finish(self):
        self._time_out = datetime.now()

    def row(self):
        out = self._time_out.strftime(self.FMT) if self._time_out else "-"
        return (self._login, self._time_in.strftime(self.FMT), out)

    def info(self):
        return "Сеанс %s %s - %s" % self.row()

    def key(self):
        return (self._time_in, self._login)

    def __bool__(self):
        return self._time_out is not None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.finish()

    @staticmethod
    def save_report(sessions, path="report.txt"):
        rows = [s.row() for s in sessions]
        w = [len("login"), len("time_in"), len("time_out")]
        for r in rows:
            for i in range(3):
                w[i] = max(w[i], len(r[i]))
        line = "+" + "-" * (sum(w) + 8) + "+"
        text = [line]
        text.append("| %-*s | %-*s | %-*s |" % (w[0], "login", w[1], "time_in", w[2], "time_out"))
        text.append("|%s|%s|%s|" % ("-" * (w[0] + 2), "-" * (w[1] + 2), "-" * (w[2] + 2)))
        for r in rows:
            text.append("| %-*s | %-*s | %-*s |" % (w[0], r[0], w[1], r[1], w[2], r[2]))
        text.append(line)
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(text) + "\n")
