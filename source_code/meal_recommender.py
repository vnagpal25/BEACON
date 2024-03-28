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
        
        self.recommendation = None
        self.goodness_score = None


    def ReadInputs(self):
        # Read Taco Bell R3
        with open('../items_data/taco_bell.json', 'r') as file:
            recipes = json.load(file)
            recipes = recipes['recipe-ids']   
        
        # Read R3 dataset
        with open('../items_data/recipe_repn.json', 'r') as file:
            file = json.load(file)
            recipes = recipes | recipes

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
        rec_constraints = self.user_request['recommendation_constraints'] # [{'meal': 'breakfast'/'lunch'/'dinner', 'time': 'HH:MM'}']
        amount_days = self.user_request['time_period']
        
        # [[Days: {Meal Type, Meal {<Beverage><MainCourse><Side>, }}]]
        meal_plan = []
        
        # iterate over the number of days
        for j in range(amount_days):
            # holds list of meals for day j
            meals = []
            
            # iterates over meal configuration for each day
            for meal_info in rec_constraints:
                meal_info = meal_info['meal_type']
                
                # Final Parsing on User Input
                meal_name = meal_info['meal_name']
                meal_time = meal_info['time']
                
                meal_config = meal_info['meal_config']
                meal_config = MealConfig(meal_config)
                
                meal_info = MealInfo(meal_name, meal_config, meal_time)
                                
                # To Write
                meal = {'meal_name': meal_info.meal_name,
                        'meal_time': meal_info.meal_time}
                
                # Random Method for Recommendation
                if meal_info.meal_config.has_beverage():
                    meal['Beverage'] = random.choice(list(self.beverage_set.keys()))
                if meal_info.meal_config.has_main_course():
                    meal["Main Course"] = random.choice(list(self.recipe_set.keys()))
                if meal_info.meal_config.has_dessert():
                    meal['Dessert'] = random.choice(list(self.recipe_set.keys()))
                if meal_info.meal_config.has_side():
                    meal['Side'] = random.choice(list(self.recipe_set.keys()))

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
        self.goodness_score = Metric.EvaluateMealRec(self.recommendation)
