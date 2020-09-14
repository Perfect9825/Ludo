import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32' : base = 'Win32GUI'

setup( name = 'Ludo',
       version = '1.0',
       description = 'Ludo is a highly simplistic version of Pachisi,'
                     'a game that originated in the 6th century in India.'
                     'This game is played by younger children all over the country.'
                     'In this board game 2 to 4, players race their tokens from start'
                     'to finish according to the dice rolls. Various variations are seen'
                     'in the way people people play Ludo.',
       author = 'Kalpesh Gole',
       executables = [Executable('ludo.py', base = base)])
