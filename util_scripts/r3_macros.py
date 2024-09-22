# add last system access to each recipe
# convert each "macro: amount" to macro: {measure: "g" amount: ""}

import json
import datetime


def find_measure_amt(s):
    num = ''
    unit = ''
    for i, ch in enumerate(s):
        if ch.isdigit() or ch == '.':
            num += ch
        else:
            unit = s[i:]
            break
    return num, unit


with open('../items_data/taco_bell.json', 'r') as file:
    tb_data = json.load(file)['recipe-ids']

with open('../items_data/mcdonalds.json', 'r') as file:
    md_data = json.load(file)['recipe-ids']

with open('../items_data/recipe_repn.json', 'r') as file:
    treat_data = json.load(file)['recipe-ids']

recipes = tb_data | md_data | treat_data

macro_types = set()
macro_values = set()
units = set()
for id, recipe in recipes.items():
    recipe['data_provenance']['last_system_access'] = datetime.datetime.now()

    if 'Total Carbohydrate' in recipe['macronutrients'].keys():
        recipe['macronutrients']['Carbohydrates'] = recipe['macronutrients'].pop(
            'Total Carbohydrate')

    if 'Sugars' in recipe['macronutrients'].keys():
        recipe['macronutrients']['Sugar'] = recipe['macronutrients'].pop(
            'Sugars')

    if 'Total Sugars' in recipe['macronutrients'].keys():
        recipe['macronutrients']['Sugar'] = recipe['macronutrients'].pop(
            'Total Sugars')

    if 'Total Fat' in recipe['macronutrients'].keys():
        recipe['macronutrients']['Fat'] = recipe['macronutrients'].pop(
            'Total Fat')

    if 'Dietary Fiber' in recipe['macronutrients'].keys():
        recipe['macronutrients']['Fiber'] = recipe['macronutrients'].pop(
            'Dietary Fiber')

    macro_types = macro_types.union(recipe['macronutrients'].keys())
    macro_values = macro_values.union(recipe['macronutrients'].values())

    for macro_name, macro_string in recipe['macronutrients'].items():
        measure, unit = find_measure_amt(macro_string)
        if unit == '%':
            unit = "% dv"

        units.add(unit)

        recipe['macronutrients'][macro_name] = {
            'measure': measure, 'unit': unit}

    recipes[id] = recipe

    if id in tb_data:
        tb_data[id] = recipe
    elif id in md_data:
        md_data[id] = recipe
    elif id in treat_data:
        treat_data[id] = recipe

tb_data = {'recipe-ids': tb_data}
md_data = {'recipe-ids': md_data}
treat_data = {'recipe-ids': treat_data}

with open('../items_data/taco_bell.json', 'w') as file:
    json.dump(tb_data, file, default=str)

with open('../items_data/mcdonalds.json', 'w') as file:
    json.dump(md_data, file, default=str)

with open('../items_data/recipe_repn.json', 'w') as file:
    json.dump(treat_data, file, default=str)
