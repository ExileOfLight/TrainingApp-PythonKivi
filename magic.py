import math
from copy import deepcopy
from prettytable import PrettyTable
from itertools import combinations


def get_sup(n, current, items, appearance_count, buys, singles, start_pos):
    if n == current:
        for i in range(start_pos + 1, len(buys)):
            singles[i] = buys[i]
            item = ""
            for each in singles:
                item += each
                if each != '':
                    item += ' '
            item = item[:-1]
            if item in items[-1]:
                appearance_count[-1][items[-1].index(item)] += 1
            else:
                items[-1].append(item)
                appearance_count[-1].append(1)
            singles[i] = ''
        return
    else:
        for i in range(start_pos + 1, len(buys)):
            i_ = i
            singles[i] = buys[i]
            get_sup(n, current + 1, items, appearance_count, buys, singles, i_)
            singles[i] = ''


def apriori(data, min_support, min_confidence, min_lift, max_number_of_items):
    for i in range(len(data)):
        for j in range(len(data[i])):
            if ' ' in data[i][j]:
                data[i][j] = data[i][j].split(' ')
                data[i][j] = '_'.join(data[i][j])
    data_n = len(data)
    f = math.ceil(min_support * data_n)
    if f < 2:
        f = 2
#     # print('f =', f)
    items = []
    appearance_count = []
    singles = [''] * max_number_of_items
    flag_pop = False
    for i in range(max_number_of_items):
        items.append([])
        appearance_count.append([])
        for buys in data:
            get_sup(i, 0, items, appearance_count, buys, singles, -1)
        shift = 0
        for j in range(0, len(appearance_count[-1])):
            if appearance_count[-1][j - shift] < f:
                appearance_count[-1].pop(j - shift)
                items[-1].pop(j - shift)
                shift += 1
        if not items[-1]:
            flag_pop = True
            break
    if flag_pop:
        items.pop()
#     #print(items)
#     #print(appearance_count)
    support_table = deepcopy(appearance_count)
    for i in range(0, len(items)):
        for j in range(0, len(items[i])):
            support_table[i][j] = round(appearance_count[i][j] / data_n, 4)
#     #print(support_table)
    rules = []
    for i in range(0, len(items)):
        rules.append([])
    for i in range(1, len(items)):  # Создание правил
        for each in items[i]:
            subject = each.split(' ')
            for singlet_rule in subject:
                rules[i].append(singlet_rule)
            for j in range(2, len(subject)):
                combs = list(combinations(subject, j))
                for comb in combs:
                    rules[i].append(comb)
    for i in range(2, len(rules)):  # Преобразование таплов в строки
        for j in range(0, len(rules[i])):
            if isinstance(rules[i][j], tuple):
                temp_string = ''
                for name in rules[i][j]:
                    temp_string += name + ' '
                rules[i][j] = temp_string[:-1]
#     #print(rules)
    confidence_table = deepcopy(rules)
    for i in range(1, len(items)):
        rules_by_item = 2 ** (i + 1) - 2
        for j in range(0, len(items[i])):
            for k in range(math.factorial(i + 1)):
                shifted_i = i
                for each in items:
                    try:
                        confidence_table[i][rules_by_item * j + k] = round(
                            appearance_count[i][j] / appearance_count[shifted_i - 1][
                                items[shifted_i - 1].index(rules[i][rules_by_item * j + k])], 4)
                    except (ValueError, IndexError):
                        shifted_i -= 1
#     #print(confidence_table)
    lift_table = deepcopy(confidence_table)

    for i in range(1, len(lift_table)):
        for j in range(0, len(lift_table[i])):
            shifted_i = i-1
            shifted_j = -(j+1)
            if i==1:
                shifted_j = j+1-(j%2)*2
            for l in range(len(items)-1):
                try:
                    lift_table[i][j] = round(
                        confidence_table[i][j] / support_table[l][
                            items[l].index(rules[i][shifted_j])], 2)
                except:
                    continue
#     #print()
#     #print('Минимальная поддержка =', min_support, "Минимальная достоверность =", min_confidence, 'Минимальный лифт =',
     #     min_lift)
    output = []
    for i in range(1, len(items)):
        rules_by_item = 2 ** (i + 1) - 2
        for j in range(0, len(items[i])):
            for k in range(rules_by_item):
                output.append([])
                output[-1].append(items[i][j])
                output[-1].append(str(support_table[i][j]))
                output[-1].append(rules[i][rules_by_item * j + k])
                output[-1].append(confidence_table[i][rules_by_item * j + k])
                output[-1].append(lift_table[i][rules_by_item * j + k])
                if output[-1][-2] < min_confidence or output[-1][-1] < min_lift:
                    output.pop()
# #    print(output)
    clmn_names = ['Набор', 'Поддержка', 'Условие', 'Достоверность', 'Лифт']
    table = PrettyTable()
    table.add_rows(output)
    table.field_names = clmn_names
    #print(table)
    return output

#apriori(food_data, 0.07, 0.3,0.001,max_number_of_items)  # Данные в scv формате, Минимальная поддержка, Минимальная достоверность, Максимум предметов в строке