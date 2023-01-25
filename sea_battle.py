from random import randint

class Dot: #создаем класс точка
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'DOT({self.x}, {self.y})' #вывод координаты в консоль

class BoardException(Exception):#создаем классы исключений
    pass

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongShipException(BoardException):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску"

class Ship: #создаем класс корабль
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o #Ориентация коробля
        self.lives = l

    @property
    def dots(self): #функция для определения точек корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot): #проверка попадания в корабль
        return shot in self.dots

class Board: #создание класса "игровая доска"
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0 #количество пораженных кораблей
        self.field = [["0"] * size for _ in range(size)]#атрибут, позволяющий хранить состояние игрового поля
        self.busy = [] #атрибут, хранящий занятые точки
        self.ships = [] #список кораблей на доске

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f'\n{i+1} | ' + ' | ' .join(row) + ' |'
        if self.hid:
            res = res.replace("■", "0") #если в точке находится корабль, заменяет 0 на ■
        return res

    def out(self,d): #проверка на то, что точка выходит за пределы игрового поля
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False): #задает контур для каждого корабля, чтобы нельзя было рядом поставить и указывало при убийстве корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)  #добавляем в список точки вокруг корабля

    def add_ship(self, ship): #создаем корабль, а также проверяем что каждая точка корабля не выходит за границы поля, а также не занята
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d) #добавляем все точки корабля в список занятых
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d): #функция выстрел
        if self.out(d):
            raise BoardOutException() #проверка на исключения
        if d in self.busy:
            raise BoardUsedException() #проверка на исключения
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots: #тут проверяем, попал ли выстрел "d" в корабль
                ship.lives -= 1
                self.field[d.x][d.y] = "X" #если попал, то на клетку присваивается X
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!') #если у корабля не осталось жизней
                    return False
                else:
                    print('Корабль ранен!') #если остались жизни
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = [] #тут собираеми все занятые точки (где стоит корабль, соседние точки итд)

    #def defeat(self):
        #return self.count == len(self.ships)

class Player: #класс игрок
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self): #в этом методе пробуем делать выстрел
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player): #класс компьютер
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5)) #тут его выстрел лежит в случайной точки (0;5) (0;5)
        print(f'Ход компьютера: {d.x+1} {d.y+1}')
        return d

class User(Player): #класс пользователь
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split() #запрашиваем координаты
            if len(cords) != 2:  #проверяем что ввели 2 координаты
                print("Введите 2 координаты: ")
                continue
            x, y = cords
            if not(x.isdigit()) or not(y.isdigit()): #проверяем что эти координаты - числа
                print("Введите числа!")
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size = 6):
        self.size = size #задаем размер доски
        pl = self.random_board() #генерируем доску для игрока
        co = self.random_board() #генерируем доску для компьютера
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self): # игровое поле, которое будет удовлетворять всем требованиям (строки, кол-во кораблей, чтобы эти корабли стояли правильно)
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self): #тут создается случайное
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self): #правила
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска компьютера:")
            print(self.us.board)
            print("-"*20)
            if num % 2 == 0:
                print("Ходит игрок!") #если номер хода четный - ходит пользователь, если нет - компьютер
                repeat = self.us.move() #вызываем метод move, который отвечает за ход
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print("-"*20)
                print("Игрок выиграл!")
                break
            if self.us.board.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()