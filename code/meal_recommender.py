from metrics import Metric
from meal_info import MealInfo
from meal_config import MealConfig
import json
import random
from config import root_dir

# TODO document all methods inputs/outupts
import sys
sys.path.append('metrics')


class MealRecommender:
    # Personalized Recommender for Particular User
    def __init__(self, user):
        self.user = user
        self.recipe_set, self.beverage_set, self.user_request = self.ReadInputs()
        self.recipe_info = self.GetRecipeInfo()
        self.beverage_names = self.GetBeverageNames()

        self.time_period = self.user_request['time_period']
        self.recommendation_constraints = self.user_request['recommendation_constraints']
        self.user_compatibilities = self.user_request['user_compatibilities']
        self.recommendation = None
        self.meal_configs = {}
        self.get_configs()

        self.goodness_score = None
        self.config_score = None
        self.dup_meal_score = None
        self.dup_day_score = None
        self.coverage_score = None

        self.score_breakdown = None

    def ReadInputs(self):
        root = root_dir()

        # with open(f'{root}/items_data/test_r3.json', 'r') as file:
        #     test_recipes = json.load(file)
        #     recipes = test_recipes['recipe-ids']

        # Read Taco Bell R3
        with open(f'{root}/items_data/taco_bell.json', 'r') as file:
            tb_recipes = json.load(file)
            recipes = tb_recipes['recipe-ids']

        with open(f'../items_data/mcdonalds.json', 'r') as file:
            mcd_recipes = json.load(file)
            recipes = recipes | mcd_recipes['recipe-ids']

        # Read R3 dataset
        with open('../items_data/recipe_repn.json', 'r') as file:
            orig_r3_recipes = json.load(file)
            recipes = recipes | orig_r3_recipes['recipe-ids']

        # Read Beverages dataset
        with open('../items_data/beverages.json', 'r') as file:
            beverages = json.load(file)
            beverages = beverages['beverage_ids']

        # Read user request
        with open(f'../user_input_data/{self.user}', 'r') as file:
            user_request = json.load(file)

        return recipes, beverages, user_request

    def RunMealRecStratRandom(self):
        # Runs Meal Recommendation Strategy to create personalized meal plan
        # [{'meal': 'breakfast'/'lunch'/'dinner', 'time': 'HH:MM'}']

        # [[Days: {Meal Type, Meal {<Beverage><MainCourse><Side>, }}]]
        meal_plan = []

        # iterate over the number of days
        for j in range(self.time_period):
            # holds list of meals for day j
            meals = []

            # iterates over meal configuration for each day
            for meal_info in self.recommendation_constraints:
                meal_info = meal_info['meal_type']

                # Final Parsing on User Input
                meal_name = meal_info['meal_name']
                meal_time = meal_info['time']

                meal_config = meal_info['meal_config']
                meal_config = MealConfig(meal_config)
                self.meal_configs[meal_name] = meal_config

                meal_info = MealInfo(meal_name, meal_config, meal_time)

                # To Write
                meal = {'meal_name': meal_info.meal_name,
                        'meal_time': meal_info.meal_time}

                # Random Method for Recommendation
                if meal_info.meal_config.has_beverage():
                    meal['Beverage'] = random.choice(
                        list(self.beverage_set.keys()))
                if meal_info.meal_config.has_main_course():
                    meal["Main Course"] = random.choice(
                        list(self.recipe_set.keys()))
                if meal_info.meal_config.has_dessert():
                    meal['Dessert'] = random.choice(
                        list(self.recipe_set.keys()))
                if meal_info.meal_config.has_side():
                    meal['Side'] = random.choice(
                        list(self.recipe_set.keys()))
                meals.append(meal)

            meals = {f'day {j + 1}': meals}
            meal_plan.append(meals)

        self.recommendation = {'meal_plan': meal_plan}
        # return meal plan
        return {'meal_plan': meal_plan}

    def WriteMealRecs(self, meal_plan=None, save_path=None):
        if save_path is None:
            save_path = f'../recommendations/recommendation_{self.user}'
        if not meal_plan:
            meal_plan = self.recommendation

        # Write meal plan to json
        with open(save_path, 'w') as file:
            json.dump(meal_plan, file)

    def EvaluateRecs(self):
        goodness_calculator = Metric(
            config_weight=1, duplicate_meal_score_weight=1, duplicate_day_score_weight=1, coverages_weight=1, constraint_weight=1)

        self.goodness_score, self.config_score, \
            self.dup_meal_score, self.dup_day_score, \
            self.coverage_score, self.user_constraint_score, self.score_breakdown, self.rec_features = goodness_calculator.EvaluateMealRec(meal_plan=self.recommendation['meal_plan'], time_period=self.time_period,
                                                                                                                                           meal_configs=self.meal_configs, rec_constraints=self.recommendation_constraints,
                                                                                                                                           bev_info=self.GetBeverageNames(), recipe_info=self.recipe_info,
                                                                                                                                           user_compatibilities=self.user_compatibilities)
        self.recommendation['goodness'] = self.goodness_score
        self.recommendation['features'] = self.rec_features

    def SetRecommendation(self, file_name):
        with open(f'../recommendations/{file_name}', 'r') as file:
            self.recommendation = json.load(file)

    def GetBeverageNames(self):
        beverage_names = {}
        for id, drink in self.beverage_set.items():
            beverage_names[id] = (drink['name'],
                                  {'hasDairy': drink['hasDairy'],
                                   'hasMeat': drink['hasMeat'],
                                   'hasNuts': drink['hasNuts']})
        return beverage_names

    def GetRecipeInfo(self):
        recipe_names = {}
        for id, recipe in self.recipe_set.items():
            recipe_names[id] = (recipe['recipe_name'], {'hasDairy': recipe['hasDairy'],
                                                        'hasMeat': recipe['hasMeat'],
                                                        'hasNuts': recipe['hasNuts']}, recipe['food_role'])
        return recipe_names

    def get_configs(self):
        for j in range(self.time_period):
            # holds list of meals for day j
            meals = []

            # iterates over meal configuration for each day
            for meal_info in self.recommendation_constraints:
                meal_info = meal_info['meal_type']

                # Final Parsing on User Input
                meal_name = meal_info['meal_name']
                meal_time = meal_info['time']

                meal_config = meal_info['meal_config']
                meal_config = MealConfig(meal_config)
                self.meal_configs[meal_name] = meal_config
