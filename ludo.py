'''
This Is Original File for Ludo Game.
'''

from tkinter import *
from random import *
import json

root = Tk()

BUTTONS_MAP = {}

class LudoButton(Button):
    def initialize(self):
        self.commands = []
        self.configure(command = self.run_command)

    def run_command(self):
        if len(self.commands) > 0:
            command = self.commands.pop(0)
            command()

    def add_command(self, command_fun):
        self.commands.append(command_fun)

    def __repr__(self):
        return "Button->" + self.commands

class Coin:
    def __init__(self, name, row, col, bg_color, house, other_coins = []):
        self.selected = False
        self.step = None
        self.reached_home = False
        self.current_step = 0
        self.step_button = None
        self.name = name
        self.bg_color = bg_color
        self.house = house
        self.other_coins = other_coins
        self.house_button = Button(root, relief=RIDGE, width=5, height=2, bg=bg_color, text=name,
                                   state=DISABLED, command = self.clicked_house_button)
        self.house_button.grid(row=row, column=col)

    def update(self, step, step_button):
        self.current_step = 0
        self.step_button = step_button
        self.selected = True
        self.step = step
        self.house_button.configure(text='', bg='gray', state=DISABLED)

    def update_step(self, step, step_button, current_step):
        if step:
            self.step = step
            self.step_button = step_button
            self.current_step = current_step

    def disable_house_button(self):
        self.house_button.configure(state = DISABLED)

    def enable_house_button(self):
        self.house_button.configure(state = NORMAL)

    def clicked_house_button(self):
        step_button, step = self.house.get_step_with_button()
        self.house.kill_coins(step_button, step)
        step.incr_house_count(self.house.house_color)
        self.house.set_current_house_label()
        step_button.configure(text = self.name, bg=self.bg_color, state=DISABLED)
        step_button.add_command(self.clicked_step_button)
        self.step_button = step_button
        self.update(step, step_button)
        self.house.disable_all_house_buttons()

    def mark_reached_home(self):
        self.house_button.configure(bg ='orange', state = DISABLED)

    def enable_step_button(self):
        if self.step_button:
            self.step_button.configure(state=NORMAL)

    def disable_step_button(self):
        if self.step_button:
            self.step_button.configure(state=DISABLED)

    def update_if_reached_home(self, step):
        if step is None:
            self.reached_home = True
            self.step_button.configure(text='', bg='white', state=DISABLED)
            self.house_button.configure(text=self.name, bg='Pink', state=DISABLED)

    def clicked_step_button(self):
        print('---')
        print(self.bg_color)
        print(self.current_step)
        print(self.house.dice_step)
        # This is the step coin is on
        old_button_name = self.house.get_step_button(self.step)
        print(old_button_name, self.step_button)
        old_step_coin_count = self.step.decr_house_count(self.house.house_color)

        # This is the step coin will move to
        step = self.house.next_step(self.current_step, self.house.dice_step)
        button = None
        if step:
            print(step.step_key)
            print(self.current_step)
            self.current_step += self.house.dice_step
            print('===> ', self.current_step)
            print(step.has_coin)
            button_name = self.house.get_step_button(step)
            button = BUTTONS_MAP[button_name]
            print(button_name, button)

            self.house.kill_coins(button, step)

            button.configure(text=self.name, bg=self.bg_color, state=DISABLED)
            button.add_command(self.clicked_step_button)

            if old_step_coin_count == 0:
                self.step_button.configure(text='', bg='white', state=DISABLED)

            step.incr_house_count(self.house.house_color)
        self.house.disable_all_house_buttons()

        self.house.set_current_house_label()

        self.update_if_reached_home(step)

        self.update_step(step, button, self.current_step)

        self.disable_other_coins_step_button()

        self.house.game_over()

    def disable_other_coins_step_button(self):
        for coin in self.other_coins:
            coin.disable_step_button()

    def killed_me(self):
        self.selected = False
        self.step = None
        self.house_button.configure(bg=self.bg_color, text=self.name)

    def change_button_state(self):
        if not self.selected:
            self.house_button.configure(state = NORMAL)

def make_step_buttons(root, r, c, rx, cx, name):
    row = r
    k = 1
    for i in range(1, cx + 1):
        col = c
        for j in range(1, rx + 1):
            l = LudoButton(root, bg='white', width=5, height=2)
            l.initialize()
            # print(l['bg'])
            BUTTONS_MAP[name + str(k)] = l
            #l['text'] = name + str(k)
            k = k + 1
            l.grid(row=row, column=col)
            col += 2
        row += 2

class House:
    def __init__(self, root, bg_color, row, col, coin_name, row_inc, col_inc, house_color, other_houses = []):
        self.bg_color = bg_color
        self.coin_name = coin_name # yellow-Y, red-R, blue-B, green-G
        self.row = row
        self.col = col
        self.row_inc = row_inc
        self.col_inc = col_inc
        self.current_house = None
        self.other_houses = other_houses
        self.board = None
        self.coin1 = Coin(coin_name, self.row, self.col, bg_color, self)
        self.coin2 = Coin(coin_name, self.row, self.col + self.col_inc, bg_color, self)
        self.coin3 = Coin(coin_name, self.row + self.row_inc, self.col, bg_color, self)
        self.coin4 = Coin(coin_name, self.row + self.row_inc, self.col + self.col_inc, bg_color, self)
        self.coin1.other_coins = [self.coin2, self.coin3, self.coin4]
        self.coin2.other_coins = [self.coin1, self.coin3, self.coin4]
        self.coin3.other_coins = [self.coin1, self.coin2, self.coin4]
        self.coin4.other_coins = [self.coin1, self.coin3, self.coin2]
        self.first_time_six = False
        self.six_played_game_started = False
        self.dice_step = 0

        json_data = json.load(open('C:\MyScripts\ludo_map2.json'))[house_color]
        self.map = {}
        self.house_color = house_color
        self.steps = []
        for i in range(56):
            s = Step('S' + str(i + 1))  # Class Step Object
            self.steps.append(s)
            self.map[s.step_key] = json_data[i]

        for j in range(55):
            self.steps[j].set_next_step(self.steps[j + 1])

    def is_yellow_house(self):
        return self.house_color == 'yellow'

    def is_red_house(self):
        return self.house_color == 'red'

    def is_blue_house(self):
        return self.house_color == 'light blue'

    def is_green_house(self):
        return self.house_color == 'light green'

    def current_house_ind(self):
        if self.is_yellow_house():
            return 0
        if self.is_red_house():
            return 1
        if self.is_blue_house():
            return 2
        if self.is_green_house():
            return 3

    def can_start_game(self, n):
        return n == 6 and self.first_time_six is False

    def get_step(self, step):
        return self.steps[step]

    def get_step_button(self, step):
        return self.map[step.step_key]

    def start_game(self, dice_step):
        self.first_time_six = True
        self.coin1.enable_step_button()
        self.coin2.enable_step_button()
        self.coin3.enable_step_button()
        self.coin4.enable_step_button()
        self.six_played_game_started = True
        self.change_buttons_state()

    def continue_game(self, n):
        if self.six_played_game_started:
            self.coin1.enable_step_button()
            self.coin2.enable_step_button()
            self.coin3.enable_step_button()
            self.coin4.enable_step_button()
            self.dice_step = n

    def set_current_house_label(self):
        CURRENT_HOUSE_LABEL.configure(text=self.current_house.house_color)

    def get_step_with_button(self):
        print('===')
        print(self.house_color)
        step = self.steps[0]
        print(step.step_key)
        step.has_coin = True
        button_name = self.map[step.step_key]
        print(step.has_coin)
        button = BUTTONS_MAP[button_name]  # in 'buttons' dictionary Button Object
        print(button_name)
        return button, step

    def __repr__(self):
        return "House->" + self.house_color

    def kill_coins(self, button, step):
        for house in self.other_houses:
            v1 = self.map[step.step_key]
            if house.coin1.step:
                house_coin1 = house.map[house.coin1.step.step_key]
                if v1 == house_coin1:
                    button.commands.clear()
                    house.coin1.killed_me()
                    house.board.reset_house()

            if house.coin2.step:
                house_coin2 = house.map[house.coin2.step.step_key]
                if v1 == house_coin2:
                    button.commands.clear()
                    house.coin2.killed_me()
                    house.board.reset_house()

            if house.coin3.step:
                house_coin3 = house.map[house.coin3.step.step_key]
                if v1 == house_coin3:
                    button.commands.clear()
                    house.coin3.killed_me()
                    house.board.reset_house()

            if house.coin4.step:
                house_coin4 = house.map[house.coin4.step.step_key]
                if v1 == house_coin4:
                    button.commands.clear()
                    house.coin4.killed_me()
                    house.board.reset_house()

    def game_over(self):
        if self.coin1.reached_home and self.coin2.reached_home and self.coin3.reached_home and self.coin4.reached_home:
            self.board.dice_button.configure(state = DISABLED)
            self.board.dice_label.configure(text=self.current_house.house_color[0] + ' Winner')
            self.board.game_over()
            self.mark_as_winner()

    def mark_as_winner(self):
        self.coin1.mark_reached_home()
        self.coin2.mark_reached_home()
        self.coin3.mark_reached_home()
        self.coin4.mark_reached_home()

    def next_step(self, i, n):
        step = self.steps[i]
        while n > 0:
            step = step.next_step
            if step is None:
                return None
            n = n - 1
        step.has_coin = True
        return step

    def change_buttons_state(self):
        self.coin1.change_button_state()
        self.coin2.change_button_state()
        self.coin3.change_button_state()
        self.coin4.change_button_state()

    def enable_all_house_buttons(self):
        self.coin1.enable_house_button()
        self.coin2.enable_house_button()
        self.coin3.enable_house_button()
        self.coin4.enable_house_button()

    def disable_all_house_buttons(self):
        self.coin1.disable_house_button()
        self.coin2.disable_house_button()
        self.coin3.disable_house_button()
        self.coin4.disable_house_button()

class Step(object):
    def __init__(self, step_key):
        self.step_key = step_key
        self.next_step = None
        self.has_coin = False
        self.yellow_house_count = 0
        self.red_house_count = 0
        self.blue_house_count = 0
        self.green_house_count = 0

    def set_next_step(self, next_step):
        self.next_step = next_step

    def incr_house_count(self, house_color):
        if house_color == 'yellow':
            self.yellow_house_count += 1

        if house_color == 'red':
            self.red_house_count += 1

        if house_color == 'light blue':
            self.blue_house_count += 1

        if house_color == 'light green':
            self.green_house_count += 1

    def decr_house_count(self, house_color):
        old_step_coin_count = 0
        if house_color == 'yellow':
            self.yellow_house_count -= 1
            old_step_coin_count = self.yellow_house_count

        if house_color == 'red':
            self.red_house_count -= 1
            old_step_coin_count = self.red_house_count

        if house_color == 'light blue':
            self.blue_house_count -= 1
            old_step_coin_count = self.blue_house_count

        if house_color == 'light green':
            self.green_house_count -= 1
            old_step_coin_count = self.green_house_count
        return old_step_coin_count

class Board(object):
    def __init__(self, root):
        self.yellow_house = House(root, 'yellow', 4, 4, 'Y', 2, 2, 'yellow')  # Class House Object
        self.red_house = House(root, 'red', 4, 22, 'R', 2, 2, 'red')  # Class House Object
        self.blue_house = House(root, 'Aqua', 22, 22, 'B', 2, 2, 'light blue')  # Class House Object
        self.green_house = House(root, 'Lime', 22, 4, 'G', 2, 2, 'light green')  # Class House Object

        self.yellow_house.other_houses = [self.red_house, self.blue_house, self.green_house]
        self.red_house.other_houses = [self.yellow_house, self.blue_house, self.green_house]
        self.blue_house.other_houses = [self.yellow_house, self.red_house, self.green_house]
        self.green_house.other_houses = [self.yellow_house, self.red_house, self.blue_house]

        self.yellow_house.board = self
        self.red_house.board = self
        self.green_house.board = self
        self.blue_house.board = self

        self.dice_button = Button(root, relief=GROOVE, width=5, height=2, text='Dice')
        self.dice_button.configure(command=self.dice)
        self.dice_button.grid(row=16, column=16)
        self.dice_label = Label(root, relief=SUNKEN, width=5, height=2)
        self.dice_label.grid(row=16, column=18)
        self.current_step = 0

        self.current_house = self.yellow_house
        self.yellow_house.current_house = self.current_house

    def reset_house(self):
        houses = [self.yellow_house, self.red_house, self.blue_house, self.green_house]
        current_house_ind = self.current_house.current_house_ind()
        print('reset_house')
        print('before ', self.current_house.house_color)
        if self.nums[0] != 6:
            if current_house_ind == 0:
                current_house_ind = 3
            else:
                current_house_ind -= 1

            self.current_house = houses[current_house_ind]

            for house in houses:
                house.current_house = self.current_house
        print('After ', self.current_house.house_color)
    def change_house(self):
        houses = [self.yellow_house, self.red_house, self.blue_house, self.green_house]
        current_house_ind = self.current_house.current_house_ind()
        print('change_house')
        print('before ', self.current_house.house_color)
        if self.current_house.six_played_game_started:
            if self.nums[0] != 6:
                if current_house_ind == 3:
                    self.current_house = houses[0]
                else:
                    self.current_house = houses[current_house_ind + 1]
        else:
            if current_house_ind == 3:
                self.current_house = houses[0]
            else:
                self.current_house = houses[current_house_ind + 1]
        print('After ', self.current_house.house_color)
        for house in houses:
            house.current_house = self.current_house

    def game_over(self):
        self.yellow_house.disable_all_house_buttons()
        self.red_house.disable_all_house_buttons()
        self.blue_house.disable_all_house_buttons()
        self.green_house.disable_all_house_buttons()

    def dice(self):
        self.nums = sample(range(1, 7), 1)
        print(self.nums)
        self.dice_label.configure(text=self.nums)
        if self.current_house.can_start_game(self.nums[0]):
            self.current_house.start_game(self.nums[0])
            if self.current_house == self.yellow_house:
                self.yellow_house.enable_all_house_buttons()
            else:
                self.yellow_house.disable_all_house_buttons()

            if self.current_house == self.red_house:
                self.red_house.enable_all_house_buttons()
            else:
                self.red_house.disable_all_house_buttons()

            if self.current_house == self.blue_house:
                self.blue_house.enable_all_house_buttons()
            else:
                self.blue_house.disable_all_house_buttons()

            if self.current_house == self.green_house:
                self.green_house.enable_all_house_buttons()
            else:
                self.green_house.disable_all_house_buttons()

        else:
            self.current_house.continue_game(self.nums[0])
            if self.nums[0] != 6:
                self.yellow_house.disable_all_house_buttons()
                self.red_house.disable_all_house_buttons()
                self.blue_house.disable_all_house_buttons()
                self.green_house.disable_all_house_buttons()
                if self.current_house.six_played_game_started:
                    CURRENT_HOUSE_LABEL.configure(text=self.current_house.house_color)
                    self.change_house()
                else:
                    self.change_house()
                    CURRENT_HOUSE_LABEL.configure(text=self.current_house.house_color)
            else:
                self.current_house.enable_all_house_buttons()
                self.change_house()

# Use lowercase for variable names

b = Board(root)

CURRENT_HOUSE_LABEL = Label(root, text='yellow', width=10, height=5)
CURRENT_HOUSE_LABEL.grid(row=18, column=16)

make_step_buttons(root, 14, 2, 6, 3, 'L')
make_step_buttons(root, 2, 14, 3, 6, 'T')
make_step_buttons(root, 14, 20, 6, 3, 'R')
make_step_buttons(root, 20, 14, 3, 6, 'B')

root.mainloop()