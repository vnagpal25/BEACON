"""
Takes in user preference information,
Generates correctly formatted data for boosted bandit method
Trains/Tests bandit model and saves results 
"""


import sys
import random
import os
import json
import shutil
import re
import subprocess
import argparse
from colorama import Fore, init


def partition(arr, num_pos, num_neg):
    # Shuffle the array
    random.shuffle(arr)

    # Create the three partitions
    pos = arr[:num_pos]
    neg = arr[num_pos: num_pos + num_neg]
    remaining = arr[num_pos + num_neg:]

    return pos, neg, remaining


def exhaustive_partition():
    """
    dairy meat nuts
    0     0    0
    0     0    1
    0     0   -1
    0     1     0
    0     1     1
    0     1     -1
    0     -1    0
    0     -1    1
    0     -1    -1
    1     0     0
    1     0     1
    1     0     -1
    1     1     0
    1     1     1
    1     1     -1
    1     -1    0
    1     -1    1
    1      -1   -1
    -1    0     0
    -1    0     1
    -1    0     -1
    -1    1     0
    -1    1     1
    -1    1     -1
    -1    -1     0
    -1    -1      1
    -1    -1     -1
    """
    # generating user opinion lists based on above exhaustive configuration (pos 1, neg -1, neutral 0)
    dairy_opinions = [0] * 9 + [1] * 9 + [-1] * 9
    meat_opinions = [0, 0, 0, 1, 1, 1, -1, -1, -1] * 3
    nut_opinions = [0, 1, -1] * 9

    # splitting opinion lists into positive_list, negative_list, and neutral_list
    user_dairy_opinions = [i+1 for i, el in enumerate(dairy_opinions) if el == 1], [i+1 for i, el in enumerate(
        dairy_opinions) if el == -1], [i+1 for i, el in enumerate(dairy_opinions) if el == 0]

    user_meat_opinions = [i+1 for i, el in enumerate(meat_opinions) if el == 1], [i+1 for i, el in enumerate(
        meat_opinions) if el == -1], [i+1 for i, el in enumerate(meat_opinions) if el == 0]

    user_nut_opinions = [i+1 for i, el in enumerate(nut_opinions) if el == 1], [i+1 for i, el in enumerate(
        nut_opinions) if el == -1], [i+1 for i, el in enumerate(nut_opinions) if el == 0]

    return user_dairy_opinions, user_meat_opinions, user_nut_opinions


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


def gen_facts(dairy_opinions, meat_opinions, nut_opinions):
    user_facts = []
    food_facts = []

    for feature_name, opinions in [('dairy', dairy_opinions),
                                   ('meat', meat_opinions),
                                   ('nuts', nut_opinions)]:
        positive, negative, _ = opinions
        for opinion, type_str in [(positive, 'positive'),
                                  (negative, 'negative')]:
            for user in opinion:
                user_facts.append(
                    f'preference(user_{user}, {type_str}_{feature_name}).')

    beverages, mcdonalds, taco_bell, treat_data = load_r3()

    for data, is_bev in ((beverages, True), (mcdonalds, False), (taco_bell, False), (treat_data, False)):
        for key, item_info in data.items():
            if item_info['hasNuts']:
                if is_bev:
                    food_facts.append(f'item(bev_{key}, has_nuts).')
                else:
                    food_facts.append(f'item(food_{key}, has_nuts).')
            if item_info['hasMeat']:
                if is_bev:
                    food_facts.append(f'item(bev_{key}, has_meat).')
                else:
                    food_facts.append(f'item(food_{key}, has_meat).')
            if item_info['hasDairy']:
                if is_bev:
                    food_facts.append(f'item(bev_{key}, has_dairy).')
                else:
                    food_facts.append(f'item(food_{key}, has_dairy).')

    return user_facts, food_facts


def gen_pairs(users, dairy_opinions, meat_opinions, nut_opinions):
    pos_pairs = []
    neg_pairs = []

    _, neg_dairy, _ = dairy_opinions
    _, neg_meat, _ = meat_opinions
    _, neg_nuts, _ = nut_opinions

    beverages, mcdonalds, taco_bell, treat_data = load_r3()

    for user in users:
        for data, is_bev in ((beverages, True), (mcdonalds, False), (taco_bell, False), (treat_data, False)):
            for key, item_info in data.items():
                if ((item_info['hasNuts'] and user in neg_nuts) or
                    (item_info['hasDairy'] and user in neg_dairy) or
                        (item_info['hasMeat'] and user in neg_meat)):
                    if is_bev:
                        neg_pairs.append(
                            f'recommendation(user_{user}, bev_{key}).')
                    else:
                        neg_pairs.append(
                            f'recommendation(user_{user}, food_{key}).')
                else:
                    if is_bev:
                        pos_pairs.append(
                            f'recommendation(user_{user}, bev_{key}).')
                    else:
                        pos_pairs.append(
                            f'recommendation(user_{user}, food_{key}).')

    return pos_pairs, neg_pairs


def save_users(users, dairy_opinions, meat_opinions, nut_opinions, trial_num, num_days):
    pos_dairy, neg_dairy, _ = dairy_opinions
    pos_meat, neg_meat, _ = meat_opinions
    pos_nuts, neg_nuts, _ = nut_opinions

    src_dir = '../user_input_data/trial0'
    dest_dir = f'../user_input_data/trial{trial_num}'

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    # Recursively copy the source directory to the destination directory
    shutil.copytree(src_dir, dest_dir)

    for user in users:
        with open('../user_input_data/user_0.json') as read_file:
            sample_user = json.load(read_file)

            if user in pos_dairy:
                sample_user["user_compatibilities"]['dairyPreference'] = 1
            elif user in neg_dairy:
                sample_user["user_compatibilities"]['dairyPreference'] = -1

            if user in pos_meat:
                sample_user["user_compatibilities"]['meatPreference'] = 1
            elif user in neg_meat:
                sample_user["user_compatibilities"]['meatPreference'] = -1

            if user in pos_nuts:
                sample_user["user_compatibilities"]['nutsPreference'] = 1
            elif user in neg_nuts:
                sample_user["user_compatibilities"]['nutsPreference'] = -1

            sample_user['time_period'] = num_days

        with open(f'{dest_dir}/user_{user}.json', 'w') as write_file:
            json.dump(sample_user, write_file, indent=2)


def split_train_test(array, per_train=0.8):
    # shuffle the array
    random.shuffle(array)

    # Determine the split index
    split_index = int(per_train * len(array))

    # Split the array into train test
    train = array[:split_index]
    test = array[split_index:]
    return train, test


def save_facts_pairs(train_facts, train_neg, train_pos, test_facts, test_neg, test_pos):
    trials = os.listdir('../boosted_bandit')
    pattern = r'trial(\d+)'
    numbers = [int(re.search(pattern, trial).group(1)) for trial in trials]

    file_num = max(numbers) + 1

    src_dir = '../boosted_bandit/trial0'
    dest_dir = f'../boosted_bandit/trial{file_num}'

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    # Recursively copy the source directory to the destination directory
    shutil.copytree(src_dir, dest_dir)

    for contents, file_name in [(train_facts, 'train_facts.txt'),
                                (train_neg, 'train_neg.txt'),
                                (train_pos, 'train_pos.txt')]:
        with open(f'../boosted_bandit/trial{file_num}/train/{file_name}', 'w') as file:
            contents = [(line + '\n') for line in contents]
            file.writelines(contents)

    for contents, file_name in [(test_facts, 'test_facts.txt'),
                                (test_neg, 'test_neg.txt'),
                                (test_pos, 'test_pos.txt')]:
        with open(f'../boosted_bandit/trial{file_num}/test/{file_name}', 'w') as file:
            contents = [(line + '\n') for line in contents]
            file.writelines(contents)

    return f'../boosted_bandit/trial{file_num}', file_num


def train_bandit(bandit_trial_path):
    train_command = ['java', '-jar', 'boostsrl.jar', '-l', '-combine',
                     '-train', 'train/', '-target', 'recommendation', '-trees', '20']

    train_result = subprocess.run(train_command, cwd=bandit_trial_path,
                                  capture_output=True, text=True)
    # Check the result
    if not train_result.returncode:
        print(
            f"Bandit in {bandit_trial_path} trained successfully. Ouput written in {bandit_trial_path}/out_train.txt")
        with open(f"{bandit_trial_path}/out_train.txt", 'w') as log_file:
            log_file.write(train_result.stdout)
    else:
        print('Error in training bandit:', train_result.stderr)
        exit()


def test_bandit(bandit_trial_path):
    test_command = ['java', '-jar', 'boostsrl.jar', '-i', '-model', 'train/models/',
                    '-test', 'test/', '-target', 'recommendation', '-aucJarPath', '.', '-trees', '20']
    test_result = subprocess.run(test_command, cwd=bandit_trial_path,
                                 capture_output=True, text=True)
    # Check the result
    if not test_result.returncode:
        print(
            f"Bandit in {bandit_trial_path} tested successfully. Ouput written in {bandit_trial_path}/out_test.txt")
        with open(f"{bandit_trial_path}/out_test.txt", 'w') as log_file:
            log_file.write(test_result.stdout)
    else:
        print('Error in testing bandit:', test_result.stderr)
        exit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_users')
    parser.add_argument('--num_pos')
    parser.add_argument('--num_neg')
    parser.add_argument('--num_days')
    parser.add_argument('--user_gen_mode')
    args = parser.parse_args()

    num_users = int(args.num_users) if args.num_users is not None else None
    num_pos = int(args.num_pos) if args.num_users is not None else None
    num_neg = int(args.num_neg) if args.num_users is not None else None
    num_days = int(args.num_days) if args.num_users is not None else None
    mode = args.user_gen_mode

    if mode not in ('random', 'exhaustive'):
        print('mode needs to be either "random" or "exhaustive"')

    # num_users, num_pos, num_neg, num_days = map(int, sys.argv[1:])
    dairy_opinions, meat_opinions, nut_opinions = None, None, None
    if mode == 'random':
        users = list(range(1, num_users + 1))
        dairy_opinions = partition(users, num_pos, num_neg)
        meat_opinions = partition(users, num_pos, num_neg)
        nut_opinions = partition(users, num_pos, num_neg)
    elif mode == 'exhaustive':
        # TODO, exhaustively generate users (27) and opinions
        users = list(range(1, 28))
        dairy_opinions, meat_opinions, nut_opinions = exhaustive_partition()

    user_facts, food_facts = gen_facts(
        dairy_opinions, meat_opinions, nut_opinions)

    pos_pairs, neg_pairs = gen_pairs(
        users, dairy_opinions, meat_opinions, nut_opinions)

    user_train, user_test = split_train_test(user_facts)
    food_train, food_test = split_train_test(food_facts)
    train_pos, test_pos = split_train_test(pos_pairs)
    train_neg, test_neg = split_train_test(neg_pairs)

    train_facts = user_train + food_train
    test_facts = user_test + food_test

    # saving facts
    bandit_trial_path, trial_num = save_facts_pairs(
        train_facts, train_neg, train_pos, test_facts, test_neg, test_pos)

    save_users(users, dairy_opinions, meat_opinions,
               nut_opinions, trial_num, num_days)

    # Logging info
    with open(f'{bandit_trial_path}/config.json', 'w') as file:
        config_dict = {
            'num_users': num_users,
            'num_pos': num_pos,
            'num_neg': num_neg
        }
        json.dump(config_dict, file, indent=2)

    # Train Bandit
    train_bandit(bandit_trial_path)

    # Test Bandit
    test_bandit(bandit_trial_path)

    # recommendation to user to generate recommendations
    init(convert=True)
    print(
          'To generate recommendations, run this command: ' + Fore.GREEN + f'python gen_recs.py {trial_num}')


if __name__ == "__main__":
    main()
