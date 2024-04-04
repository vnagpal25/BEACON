# TODO document all methods inputs/outupts

import random
import json
from meal_config import MealConfig
from meal_info import MealInfo
from metrics import Metric

class MealRecommender:  
    # Personalized Recommender for Particular User
    def __init__(self, user):
        self.user = user
        self.recipe_set, self.beverage_set, self.user_request = self.ReadInputs()
        self.recipe_names = self.GetRecipeNames()
        self.beverage_names = self.GetBeverageNames()

        self.time_period = 0
        self.meal_configs = {}
        self.recommendation_constraints = []
        self.recommendation = None
        self.goodness_score = None
        self.config_score = None
        self.dup_score = None
        self.coverage_score = None


    def ReadInputs(self):
        # Read Taco Bell R3
        with open('../items_data/taco_bell.json', 'r') as file:
            tb_recipes = json.load(file)
            recipes = tb_recipes['recipe-ids']   
        
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


    def RunMealRecStrat(self):
        # Runs Meal Recommendation Strategy to create personalized meal plan
        self.recommendation_constraints = self.user_request['recommendation_constraints'] # [{'meal': 'breakfast'/'lunch'/'dinner', 'time': 'HH:MM'}']
        self.time_period = self.user_request['time_period']
        
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
                    meal['Beverage'] = self.beverage_names[random.choice(list(self.beverage_set.keys()))]
                if meal_info.meal_config.has_main_course():
                    meal["Main Course"] = self.recipe_names[random.choice(list(self.recipe_set.keys()))]
                if meal_info.meal_config.has_dessert():
                    meal['Dessert'] = self.recipe_names[random.choice(list(self.recipe_set.keys()))]
                if meal_info.meal_config.has_side():
                    meal['Side'] = self.recipe_names[random.choice(list(self.recipe_set.keys()))]

                meals.append(meal)
            
            meals = {f'day {j + 1}': meals}
            meal_plan.append(meals)        
        
        self.recommendation = meal_plan
        # return meal plan
        return meal_plan


    def WriteMealRecs(self, meal_plan=None):
        if not meal_plan:
            meal_plan = self.recommendation
        
        # Write meal plan to json
        with open(f'../recommendations/recommendation_{self.user}', 'w') as file:
            json.dump(meal_plan, file)


    def EvaluateRecs(self):
        goodness_calculator = Metric(config_weight=1, duplicates_weight=1, coverages_weight=1)
        self.goodness_score, self.config_score, self.dup_score, self.coverage_score = goodness_calculator.EvaluateMealRec(meal_plan = self.recommendation, time_period=self.time_period, \
                                                                  meal_configs=self.meal_configs, rec_constraints=self.recommendation_constraints, \
                                                                  bev_names = self.GetBeverageNames(), recipe_names = self.GetRecipeNames())
        

    def GetBeverageNames(self):    
        beverage_names = {}
        for id, drink in self.beverage_set.items():
          beverage_names[id] = drink['name']
        return beverage_names
    

    def GetRecipeNames(self):
        recipe_names = {}
        for id, recipe in self.recipe_set.items():
          recipe_names[id] = recipe['recipe_name']
        return recipe_names