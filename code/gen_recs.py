"""
BSD 2-Clause License

Copyright (c) 2024, AI4Society Research Group

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
Takes in bandit trial number and generates recommendations (both bandit, random, and sequential) and evaluates them and saves the results
"""

import re
import sys
import json
import random
import shutil
import os
from meal_recommender import MealRecommender
import statistics
import csv


def load_r3() -> tuple[dict, dict, dict, dict]:
    # Loading data
    beverages = json.load(open('../items_data/beverages.json'))
    beverages = beverages['beverage_ids']

    mcdonalds = json.load(open('../items_data/mcdonalds.json'))
    mcdonalds = mcdonalds['recipe-ids']

    taco_bell = json.load(open('../items_data/taco_bell.json'))
    taco_bell = taco_bell['recipe-ids']

    treat_data = json.load(open('../items_data/recipe_repn.json'))
    treat_data = treat_data['recipe-ids']

    return beverages, mcdonalds, taco_bell, treat_data


def get_highest_prob_foods(items_probs, num_users):
    _, mcdonalds, taco_bell, treat_data = load_r3()
    food_r3 = taco_bell.copy()
    food_r3.update(treat_data)
    food_r3.update(mcdonalds)

    user_items = {i: {'Main Course': [], 'Side': [], 'Dessert': []}
                  for i in range(1, num_users + 1)}

    for user, item, prob in items_probs:
        # get item roles
        item_roles = food_r3[item]['food_role']
        for role in item_roles:
            if role == 'Beverage':
                continue
            user_items[int(user)][role].append((item, float(prob)))

    rec_user_items = {i: {'Main Course': [], 'Side': [],
                          'Dessert': []} for i in range(1, num_users + 1)}

    for user, role_dict in user_items.items():
        for role, role_items in role_dict.items():
            highest_prob = 0
            for item, prob in role_items:
                if prob > highest_prob:
                    highest_prob = prob
            highest_items = [item for item,
                             prob in role_items if prob == highest_prob]
            rec_user_items[user][role] = highest_items

    for user, role_dict in rec_user_items.items():
        empty = []
        non_empty = []
        for key, val in role_dict.items():
            if len(val) == 0:
                empty.append(key)
            else:
                non_empty.append(key)

        for empty_role in empty:
            role_dict[empty_role] = random.choice(
                [rec_user_items[user][non_empty_role] for non_empty_role in non_empty])

    return rec_user_items


def get_highest_prob_bevs(items_probs, num_users):
    user_items = {i: [] for i in range(1, num_users + 1)}

    for user, item, prob in items_probs:
        user_items[int(user)].append((item, float(prob)))

    rec_user_items = {i: [] for i in range(1, num_users + 1)}

    for user, items in user_items.items():
        highest_prob = 0
        for item, prob in items:
            if prob > highest_prob:
                highest_prob = prob
        highest_items = [item for item, prob in items if prob == highest_prob]
        rec_user_items[user] = highest_items

    return rec_user_items


def gen_bandit_recs(trial_num, num_users):
    with open(f'../boosted_bandit/trial{trial_num}/test/results_recommendation.db', 'r') as rec_file:
        recs = rec_file.readlines()

    pos_recs = [rec for rec in recs if not rec.startswith('!')]
    neg_recs = [rec[1:] for rec in recs if rec.startswith('!')]
    all_recs = pos_recs + neg_recs

    pattern = r'\d+\.?\d*'
    items_and_probs = [tuple(re.findall(pattern, rec)) for rec in all_recs]

    # get a list of the higest probability beverages and items
    # rec_user_bevs = get_highest_prob_items([rec for i, rec in enumerate(
    #     items_and_probs) if 'bev' in all_recs[i]], num_users)

    rec_user_bevs = get_highest_prob_bevs([rec for i, rec in enumerate(
        items_and_probs) if 'bev' in all_recs[i]], num_users)

    # rec_user_foods = get_highest_prob_items([rec for i, rec in enumerate(
    #     items_and_probs) if 'food' in all_recs[i]], num_users)

    rec_user_foods = get_highest_prob_foods([rec for i, rec in enumerate(
        items_and_probs) if 'food' in all_recs[i]], num_users)

    src_dir = '../recommendations/trial0'
    
    if not os.path.isdir(src_dir):
      os.makedirs(src_dir)
    
    if not os.path.isdir(os.path.join(src_dir, 'bandit_recs')):
      os.makedirs(os.path.join(src_dir, 'bandit_recs'))
      
    if not os.path.isdir(os.path.join(src_dir, 'eval')):
      os.makedirs(os.path.join(src_dir, 'eval'))

    if not os.path.isdir(os.path.join(src_dir, 'random_recs')):
      os.makedirs(os.path.join(src_dir, 'random_recs'))

    if not os.path.isdir(os.path.join(src_dir, 'sequential_recs')):
      os.makedirs(os.path.join(src_dir, 'sequential_recs'))
    
    dest_dir = f'../recommendations/trial{trial_num}'

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    # Recursively copy the source directory to the destination directory
    shutil.copytree(src_dir, dest_dir)

    for i in range(1, num_users + 1):
        bevs = rec_user_bevs[i]
        foods = rec_user_foods[i]

        with open(f"../user_input_data/trial{trial_num}/user_{i}.json", 'r') as file:
            user_info = json.load(file)
            num_days = user_info['time_period']

        rec = [{f"day {day_num}": [{"meal_name": "breakfast", "meal_time": "9:00", "Beverage": "", "Main Course": ""},
                                   {"meal_name": "lunch", "meal_time": "13:00",
                                    "Beverage": "", "Main Course": "", "Side": ""},
                                   {"meal_name": "dinner", "meal_time": "20:00", "Beverage": "", "Main Course": "", "Dessert": "", "Side": ""}]} for day_num in range(1, num_days + 1)]

        for j, day in enumerate(rec, 1):
            day_rec = day[f'day {j}']
            for meal in day_rec:
                if "Beverage" in meal:
                    try:
                        meal["Beverage"] = random.choice(bevs)
                    except:
                        print(i, rec_user_bevs)
                        beverages, _, _, _ = load_r3()
                        meal["Beverage"] = random.choice(
                            list(beverages.keys()))

                if "Main Course" in meal:
                    meal["Main Course"] = random.choice(foods['Main Course'])

                if "Side" in meal:
                    meal["Side"] = random.choice(foods['Side'])

                if "Dessert" in meal:
                    meal["Dessert"] = random.choice(foods['Dessert'])

        rec = {"meal_plan": rec}
        with open(f"../recommendations/trial{trial_num}/bandit_recs/recommendation_user_{i}.json", "w") as file:
            json.dump(rec, file, indent=2)
    with open(f"../recommendations/trial{trial_num}/bandit_recs/user_preferences.json", "w") as file:
        json.dump(rec_user_foods, file, indent=2)


def gen_random_recs(trial_num, num_users):
    for i in range(1, num_users + 1):
        recommender = MealRecommender(f'trial{trial_num}/user_{i}.json')
        meal_plan = recommender.RunMealRecStratRandom()
        recommender.WriteMealRecs(
            meal_plan, f'../recommendations/trial{trial_num}/random_recs/recommendation_user_{i}.json')


def gen_sequential_recs(trial_num, num_users):
    beverages, mcdonalds, taco_bell, treat_data = load_r3()
    food_items = mcdonalds.copy()
    food_items.update(taco_bell)
    food_items.update(treat_data)

    beverages = list(beverages.keys())
    food_items = list(food_items.keys())

    beverage_num = 0
    food_num = 0

    for i in range(1, num_users + 1):
        with open(f"../user_input_data/trial{trial_num}/user_{i}.json", 'r') as file:
            user_info = json.load(file)
            num_days = user_info['time_period']

        rec = [{f"day {day_num}": [{"meal_name": "breakfast", "meal_time": "9:00", "Beverage": "", "Main Course": ""},
                                   {"meal_name": "lunch", "meal_time": "13:00",
                                    "Beverage": "", "Main Course": "", "Side": ""},
                                   {"meal_name": "dinner", "meal_time": "20:00", "Beverage": "", "Main Course": "", "Dessert": "", "Side": ""}]} for day_num in range(1, num_days + 1)]

        for j, day in enumerate(rec, 1):
            day_rec = day[f'day {j}']
            for meal in day_rec:
                if "Beverage" in meal:
                    if beverage_num == len(beverages):
                        beverage_num = 0
                    meal["Beverage"] = beverages[beverage_num]
                    beverage_num += 1

                if "Main Course" in meal:
                    if food_num == len(food_items):
                        food_num = 0
                    meal["Main Course"] = food_items[food_num]
                    food_num += 1

                if "Side" in meal:
                    if food_num == len(food_items):
                        food_num = 0
                    meal["Side"] = food_items[food_num]
                    food_num += 1

                if "Dessert" in meal:
                    if food_num == len(food_items):
                        food_num = 0
                    meal["Dessert"] = food_items[food_num]
                    food_num += 1

        rec = {"meal_plan": rec}
        with open(f"../recommendations/trial{trial_num}/sequential_recs/recommendation_user_{i}.json", "w") as file:
            json.dump(rec, file, indent=2)


def evaluate_recs(goodness_scores, file_path):

    user_constraint_coverages = []
    meal_coverages = []
    duplicate_day_scores = []
    duplicate_meal_scores = []

    for user_day in goodness_scores.values():
        for day in user_day.values():
            user_constraint_coverages.extend(day['user_constraint_coverages'])
            meal_coverages.extend(day['meal_coverages'])
            duplicate_day_scores.append(day['duplicate_day_score'])
            duplicate_meal_scores.extend(day['duplicate_meal_scores'])

    avg_user_constraint_score = statistics.mean(user_constraint_coverages)
    avg_duplicate_day_score = statistics.mean(duplicate_day_scores)
    avg_duplicate_meal_score = statistics.mean(duplicate_meal_scores)
    avg_meal_coverage_score = statistics.mean(meal_coverages)

    # future extension, combinatorially generate if more scores are added to the metric
    summary_dict = {"score_uc": avg_user_constraint_score,
                    "score_dm": avg_duplicate_meal_score,
                    "score_mc": avg_meal_coverage_score,
                    'score_uc_dm_mc': statistics.mean(
                        [avg_user_constraint_score, avg_duplicate_meal_score, avg_meal_coverage_score]),
                    "score_uc_dm": statistics.mean([avg_user_constraint_score, avg_duplicate_meal_score]),
                    "score_uc_mc": statistics.mean([avg_user_constraint_score, avg_meal_coverage_score]),
                    "score_dm_mc": statistics.mean([avg_duplicate_meal_score, avg_meal_coverage_score]),
                    "score_dd (n/a)": avg_duplicate_day_score}

    goodness_scores.update(summary_dict)

    with open(file_path, 'w') as file:
        json.dump(goodness_scores, file)

    return summary_dict


def main():
    bandit_trial_num = int(sys.argv[1])

    with open(f'../boosted_bandit/trial{bandit_trial_num}/config.json', 'r') as file:
        config_dict = json.load(file)

    num_users = int(config_dict['num_users'])

    # Recs will be saved in ../recommendations/trialNum
    gen_bandit_recs(bandit_trial_num, num_users)

    gen_random_recs(bandit_trial_num, num_users)

    gen_sequential_recs(bandit_trial_num, num_users)

    random_goodness = {}
    sequential_goodness = {}
    bandit_goodness = {}

    # Evaluate Recs
    for i in range(1, num_users + 1):
        user_reco_evaluator = MealRecommender(
            f'trial{bandit_trial_num}/user_{i}.json')

        random_rec = f'trial{bandit_trial_num}/random_recs/recommendation_user_{i}.json'
        sequential_rec = f'trial{bandit_trial_num}/sequential_recs/recommendation_user_{i}.json'
        bandit_rec = f'trial{bandit_trial_num}/bandit_recs/recommendation_user_{i}.json'

        user_reco_evaluator.SetRecommendation(random_rec)
        user_reco_evaluator.EvaluateRecs()
        random_goodness[f"{user_reco_evaluator.recommendation['goodness']}_{i}"] = user_reco_evaluator.score_breakdown
        print('------------')

        user_reco_evaluator.SetRecommendation(sequential_rec)
        user_reco_evaluator.EvaluateRecs()
        sequential_goodness[f"{user_reco_evaluator.recommendation['goodness']}_{i}"] = user_reco_evaluator.score_breakdown
        print('------------')

        user_reco_evaluator.SetRecommendation(bandit_rec)
        user_reco_evaluator.EvaluateRecs()
        bandit_goodness[f"{user_reco_evaluator.recommendation['goodness']}_{i}"] = user_reco_evaluator.score_breakdown
        print('------------')

    bandit_summary = evaluate_recs(
        bandit_goodness, f'../recommendations/trial{bandit_trial_num}/eval/bandit_res.json')

    random_summary = evaluate_recs(
        random_goodness, f'../recommendations/trial{bandit_trial_num}/eval/random_res.json')

    sequential_summary = evaluate_recs(
        sequential_goodness, f'../recommendations/trial{bandit_trial_num}/eval/sequential_res.json')

    results = {'bandit': bandit_summary, 'random': random_summary,
               'sequential': sequential_summary}

    csv_file = f'../recommendations/trial{bandit_trial_num}/eval/results.csv'

    # Extract the field names (column names) from the first dictionary
    fieldnames = list(next(iter(results.values())).keys())

    # Insert 'row_label' at the beginning of the fieldnames list for the row labels
    fieldnames.insert(0, 'row_label')

    # Write to CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the data
        for row_label, row_data in results.items():
            # Add the row label to the row data
            row_data_with_label = {'row_label': row_label, **row_data}
            writer.writerow(row_data_with_label)


if __name__ == "__main__":
    main()
