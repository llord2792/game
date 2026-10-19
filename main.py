import getpass
import flet as ft

from game import Game, Player, Session, MyMap


class Title(ft.Text):
    def __init__(self, text):
        super().__init__(text, size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400,
                         text_align=ft.TextAlign.CENTER)


class Status(ft.Text):
    def __init__(self):
        super().__init__("", size=16, text_align=ft.TextAlign.CENTER)

    def say(self, text, color=ft.Colors.WHITE):
        self.value = text
        self.color = color


class CellButton(ft.Container):
    def __init__(self, cell, on_click):
        super().__init__(width=90, height=90, border_radius=12, bgcolor=ft.Colors.BLUE_GREY_900,
                         alignment=ft.Alignment(0, 0), on_click=on_click, ink=True)
        self.cell = cell
        self.data = cell.index()
        self.label = ft.Text("", size=36, weight=ft.FontWeight.BOLD)
        self.content = self.label

    def refresh(self, hit=False):
        self.label.value = self.cell.get_mark()
        self.label.color = ft.Colors.BLUE_300 if self.cell.get_mark() == "X" else ft.Colors.CYAN_300
        self.bgcolor = ft.Colors.BLUE_800 if hit else ft.Colors.BLUE_GREY_900


class BoardView(ft.Column):
    def __init__(self, board, on_click):
        super().__init__(spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        self.buttons = [CellButton(c, on_click) for c in board]
        for r in range(3):
            self.controls.append(ft.Row(self.buttons[r * 3:r * 3 + 3], spacing=8,
                                        alignment=ft.MainAxisAlignment.CENTER))

    def refresh(self, line=()):
        for b in self.buttons:
            b.refresh(b.data in line)


class ActionButton(ft.Button):
    def __init__(self, text, on_click, color=ft.Colors.BLUE_600):
        super().__init__(text, on_click=on_click, bgcolor=color, color=ft.Colors.WHITE,
                         height=42, width=150)


class LevelSelect(ft.Dropdown):
    def __init__(self, on_select):
        super().__init__(label="Сложность", value="Нормально", width=200, on_select=on_select,
                         options=[ft.DropdownOption("Легко"), ft.DropdownOption("Нормально"),
                                  ft.DropdownOption("Сложно")])


class WinsBar(ft.ProgressBar):
    GOAL = 5

    def __init__(self):
        super().__init__(value=0, width=200, height=10, color=ft.Colors.BLUE_400,
                         bgcolor=ft.Colors.BLUE_GREY_900)

    def show(self, wins):
        self.value = min(wins, self.GOAL) / self.GOAL


class ScoreTable(ft.DataTable):
    def __init__(self):
        super().__init__(columns=[ft.DataColumn(ft.Text("Игрок")), ft.DataColumn(ft.Text("Победы"))],
                         width=220, heading_row_height=36, data_row_max_height=36)

    def fill(self, scores):
        self.rows = []
        for name, wins in sorted(scores.items(), key=lambda x: -x[1]):
            self.rows.append(ft.DataRow([ft.DataCell(ft.Text(name)), ft.DataCell(ft.Text(str(wins)))]))


class SidePanel(ft.Column):
    def __init__(self, level, bar, table, new_btn):
        super().__init__(spacing=14, width=240, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.controls = [level, ft.Text("Победы за сеанс"), bar, ft.Divider(), ft.Text("Таблица лидеров"),
                         table, new_btn]


class TopBar(ft.AppBar):
    def __init__(self, login):
        super().__init__(title=ft.Text(f"Крестики-нолики — {login}"), bgcolor=ft.Colors.BLUE_GREY_900,
                         center_title=True)


class Panel(ft.Container):
    def __init__(self, content):
        super().__init__(content=content, padding=20, border_radius=16, bgcolor=ft.Colors.BLACK_26)


class App:
    def __init__(self, page):
        self.page = page
        self.login = getpass.getuser()
        self.session = Session(self.login)
        self.sessions = [self.session]
        self.scores = MyMap()
        self.load_scores()
        self.human = Player(self.login, "X")
        self.computer = Player("Компьютер", "O")
        self.players = (self.human, self.computer)
        self.game = Game(self.human, self.computer)

        self.status = Status()
        self.board = BoardView(self.game.get_board(), self.click)
        self.level = LevelSelect(self.change_level)
        self.bar = WinsBar()
        self.table = ScoreTable()
        self.new_btn = ActionButton("Новая игра", self.new_game)
        self.side = SidePanel(self.level, self.bar, self.table, self.new_btn)

        page.title = "Крестики-нолики"
        page.theme_mode = ft.ThemeMode.DARK
        page.window.width = 720
        page.window.height = 560
        page.window.prevent_close = True
        page.window.on_event = self.window_event
        page.on_disconnect = self.disconnect
        page.appbar = TopBar(self.login)
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.add(
            Title("Крестики-нолики"),
            self.status,
            ft.Row([Panel(self.board), self.side], alignment=ft.MainAxisAlignment.CENTER,
                   vertical_alignment=ft.CrossAxisAlignment.START, spacing=24),
        )
        self.refresh()
        self.status.say(f"{self.login}, ваш ход. Вы играете за X.")
        page.update()

    def load_scores(self):
        try:
            with open("scores.txt", encoding="utf-8") as f:
                for line in f:
                    if ";" in line:
                        name, wins = line.strip().rsplit(";", 1)
                        self.scores[name] = int(wins)
        except FileNotFoundError:
            pass

    def save_scores(self):
        with open("scores.txt", "w", encoding="utf-8") as f:
            for name, wins in self.scores.items():
                f.write(f"{name};{wins}\n")

    def refresh(self):
        self.board.refresh(self.game.get_board().win_line())
        self.bar.show(self.human.get_wins())
        self.table.fill(self.scores)

    def click(self, e):
        if not self.game.move(e.control.data):
            return
        if self.game.is_over():
            r = self.game.get_result()
            if r == "win":
                self.scores[self.login] = self.scores.get(self.login, 0) + 1
                self.save_scores()
                self.status.say("Вы победили!", ft.Colors.GREEN_400)
            elif r == "lose":
                self.status.say("Победил компьютер", ft.Colors.RED_400)
            else:
                self.status.say("Ничья", ft.Colors.AMBER_400)
        else:
            self.status.say("Ваш ход")
        self.refresh()
        self.page.update()

    def change_level(self, e):
        self.game.set_level(self.level.value)

    def new_game(self, e):
        self.game.restart()
        self.status.say("Новая партия. Ваш ход.")
        self.refresh()
        self.page.update()

    def finish(self):
        if self.session.get_time_out() is None:
            self.session.finish()
            Session.save_report(self.sessions)
            self.save_scores()

    async def window_event(self, e):
        if e.type == ft.WindowEventType.CLOSE:
            self.finish()
            await self.page.window.destroy()

    def disconnect(self, e):
        self.finish()


if __name__ == "__main__":
    ft.run(App)
