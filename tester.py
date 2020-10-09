player_1 = ['a', 'b', 'c', 'd', 'e']
player_2 = ['f', 'e', 'x', 'd', 'r']

def validate_word(word):
    sequence_list = []
    for letters in word:
        if letters in player_1 and letters in player_2:
            sequence_list.append(3)
        elif letters in player_1:
            sequence_list.append(1):
        elif letters in player_2:
            sequence_list.append(2)
        else:
            sequence_list.append(0)
    return sequence_list

print(validate_word(player_1, player_2))
