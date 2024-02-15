import random
import json
from meal_config import MealConfig
from meal_info import MealInfo


class MealRecommender:  
    # Personalized Recommender for Particular User
    def __init__(self, user):
        self.user = user
        self.recipe_set, self.beverage_set, self.user_request = self.ReadInputs()


    def ReadInputs(self):
        # Read R3 dataset
        with open('../data/recipe_repn.json', 'r') as file:
            recipes = json.load(file)
            recipes = recipes['recipe-ids']   
        
        # Read Beverages dataset
        with open('../data/beverages.json', 'r') as file:
            beverages = json.load(file)
            beverages = beverages['beverage_ids']
            
        # Read user request
        with open(f'../data/{self.user}', 'r') as file:
            user_request = json.load(file)

        return recipes, beverages, user_request


    def RunMealRecStrat(self):
        # Runs Meal Recommendation Strategy to create personalized meal plan
        
        amount_meals = self.user_request['recommendations_per_day'] # integer
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
                    meal['beverage'] = random.choice(list(self.beverage_set.keys()))
                if meal_info.meal_config.has_main_course():
                    meal['main_course'] = random.choice(list(self.recipe_set.keys()))
                if meal_info.meal_config.has_dessert():
                    meal['dessert'] = random.choice(list(self.recipe_set.keys()))
                if meal_info.meal_config.has_side():
                    meal['side'] = random.choice(list(self.recipe_set.keys()))

                meals.append(meal)
            
            meals = {f'day {j + 1}': meals}
            meal_plan.append(meals)        
        
        # return meal plan
        return meal_plan


    def WriteMealRecs(self, meal_plan):
        # Write meal plan to json
        self.user
        with open(f'../data/recommendation_{self.user}', 'w') as file:
            json.dump(meal_plan, file)