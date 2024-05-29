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


def load_r3():
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


def get_highest_prob_items(items_probs, num_users):
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
    rec_user_bevs = get_highest_prob_items([rec for i, rec in enumerate(
        items_and_probs) if 'bev' in all_recs[i]], num_users)

    rec_user_foods = get_highest_prob_items([rec for i, rec in enumerate(
        items_and_probs) if 'food' in all_recs[i]], num_users)

    src_dir = '../recommendations/trial0'
    dest_dir = f'../recommendations/trial{trial_num}'

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    # Recursively copy the source directory to the destination directory
    shutil.copytree(src_dir, dest_dir)

    for i in range(1, num_users + 1):
        bevs = rec_user_bevs[i]
        foods = rec_user_foods[i]
        rec = [{"day 1": [{"meal_name": "breakfast", "meal_time": "9:00", "Beverage": "", "Main Course": ""},
                          {"meal_name": "lunch", "meal_time": "13:00",
                              "Beverage": "", "Main Course": "", "Side": ""},
                          {"meal_name": "dinner", "meal_time": "20:00", "Beverage": "", "Main Course": "", "Dessert": "", "Side": ""}]}]

        for j, day in enumerate(rec, 1):
            day_rec = day[f'day {j}']
            for meal in day_rec:
                if "Beverage" in meal:
                    meal["Beverage"] = random.choice(bevs)

                if "Main Course" in meal:
                    meal["Main Course"] = random.choice(foods)

                if "Side" in meal:
                    meal["Side"] = random.choice(foods)

                if "Dessert" in meal:
                    meal["Dessert"] = random.choice(foods)

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
    food_items = mcdonalds | taco_bell | treat_data

    beverages = list(beverages.keys())
    food_items = list(food_items.keys())

    beverage_num = 0
    food_num = 0

    for i in range(1, num_users + 1):
        rec = [{"day 1": [{"meal_name": "breakfast", "meal_time": "9:00", "Beverage": "", "Main Course": ""},
                          {"meal_name": "lunch", "meal_time": "13:00",
                           "Beverage": "", "Main Course": "", "Side": ""},
                          {"meal_name": "dinner", "meal_time": "20:00", "Beverage": "", "Main Course": "", "Dessert": "", "Side": ""}]}]
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

    for day in goodness_scores.values():
        day = day['day 1']
        user_constraint_coverages.extend(day['user_constraint_coverages'])
        meal_coverages.extend(day['meal_coverages'])
        duplicate_day_scores.append(day['duplicate_day_score'])
        duplicate_meal_scores.extend(day['duplicate_meal_scores'])

    avg_user_constraint_score = statistics.mean(user_constraint_coverages)
    avg_duplicate_day_score = statistics.mean(duplicate_day_scores)
    avg_duplicate_meal_score = statistics.mean(duplicate_meal_scores)
    avg_meal_coverage_score = statistics.mean(meal_coverages)

    goodness_scores |= {"Average User Constraint Score": avg_user_constraint_score,
                        "Average Duplicate Day Score": avg_duplicate_day_score,
                        "Average Duplicate Meal Score": avg_duplicate_meal_score,
                        "Average Meal Coverage Score": avg_meal_coverage_score}

    with open(file_path, 'w') as file:
        json.dump(goodness_scores, file)


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

    evaluate_recs(
        bandit_goodness, f'../recommendations/trial{bandit_trial_num}/eval/bandit_res.json')

    evaluate_recs(
        random_goodness, f'../recommendations/trial{bandit_trial_num}/eval/random_res.json')

    evaluate_recs(
        sequential_goodness, f'../recommendations/trial{bandit_trial_num}/eval/sequential_res.json')


if __name__ == "__main__":
    main()
