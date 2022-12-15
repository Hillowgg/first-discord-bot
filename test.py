import random
import pprint


def minesweeper(mines: int):
    mine = '💥'
    field = [*[mine for i in range(mines)], *[0 for i in range(100 - mines)]]
    random.shuffle(field)
    completedField = []
    emojies = {
        0: '0️⃣',
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣',
        6: '6️⃣',
        7: '7️⃣',
        8: '8️⃣',
        mine: '💥'
    }
    text = f'**Minesweeper**\nПоле: `10х10`\nКоличество мин: `{mines}`\n'
    for i in range(0, 100, 10):
        completedField.append(field[i:i + 10])
    for i in range(len(completedField)):
        for g in range(len(completedField[i])):
            if completedField[i][g] == mine:
                if g < len(completedField[i]) - 1 and isinstance(completedField[i][g + 1], int): completedField[i][g + 1] += 1  # further + 1
                if g > 0 and isinstance(completedField[i][g - 1], int): completedField[i][g - 1] += 1  # previous + 1
                if i > 0:
                    if g < len(completedField[i]) - 1 and isinstance(completedField[i - 1][g + 1], int): completedField[i - 1][g + 1] += 1  # further + 1
                    if g > 0 and isinstance(completedField[i - 1][g - 1], int): completedField[i - 1][g - 1] += 1  # previous + 1
                    if isinstance(completedField[i - 1][g], int): completedField[i - 1][g] += 1
                if i < len(completedField[i]) - 1:
                    if g < len(completedField[i]) - 1 and isinstance(completedField[i + 1][g + 1], int): completedField[i + 1][g + 1] += 1  # further + 1
                    if g > 0 and isinstance(completedField[i + 1][g - 1], int): completedField[i + 1][g - 1] += 1  # previous + 1
                    if isinstance(completedField[i + 1][g], int): completedField[i + 1][g] += 1
    for i in completedField:
        for g in i:
            text += f'||{emojies[g]}||'
        text += '\n'

    text += '\n*Made by: Hillow*'
    print(text)


minesweeper(10)
