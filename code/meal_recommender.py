# TODO document all methods inputs/outupts

import random
import json
from meal_config import MealConfig
from meal_info import MealInfo


class MealRecommender:  
    # Personalized Recommender for Particular User
    def __init__(self, user):
        self.user = user
        self.recipe_set, self.beverage_set, self.user_request = self.ReadInputs()
        self.recommendation = None

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
   

    def EvaluateMealRec(self, meal_plan=None):
        # TODO, make evaluation metrics more configurable, not hard coded
        # i.e., user may want redundancy, so shouldn't be penalized

        if not meal_plan:
            meal_plan = self.recommendation

        
        def ConfigScore(meal_plan_):
          score = 0
          total_possible_score = 0
          good = len(meal_plan_) == self.user_request['time_period']
          if good:
              score += 1
          total_possible_score += 1

          for i, out_day in enumerate(meal_plan_, 1):
              # Get each day's recommendations
              out_day = out_day[f'day {i}']
              
              for inp, out in zip(self.user_request['recommendation_constraints'], out_day):
                  inp = inp['meal_type']
                  
                  good &= inp['meal_name'] == out['meal_name']
                  if good:
                      score += 1
                  total_possible_score += 1

                  good &= inp['time'] == out['meal_time']
                  if good:
                      score += 1
                  total_possible_score += 1

                  out.pop('meal_name')
                  out.pop('meal_time')

                  good &= set(inp['meal_config']) == set(list(out.keys()))
                  if good :
                      score += 1
                  total_possible_score += 1

          return score / total_possible_score
        
        # Checks if Meal Config is satisfied, a number between 0 and 1
        config_quality_score = ConfigScore(meal_plan)
        

        def NumDuplicates(meal_plan_):
            violations = 0
            total_chances = 0
            for i, day_plan in enumerate(meal_plan_, 1):
                day_plan = day_plan[f'day {i}']
                food_items = set()
                bev_items = set()

                for meal in day_plan:
                    
                    if 'Beverage' in meal:
                        if meal['Beverage'] in bev_items:
                            violations += 1
                        total_chances += 1
                        bev_items.add(meal['Beverage'])
                    for food_key in ['Main Course', 'Dessert', 'Side']:
                        if food_key in meal:
                            if meal[food_key] in food_items:
                                violations += 1
                            total_chances += 1 
                            food_items.add(meal[food_key])
            return violations / total_chances
        
        # Check for number of duplicates in meal plan
        # Rule by Vansh Nagpal: same meal item showing up twice in same day is considered a duplicate
        # between 0 and 1
        violations = NumDuplicates(meal_plan)

        # TODO Calculate violations based on calories and macronutrients

        # TODO Calculate violations based on allergens

        # TODO discuss with group if this makes sense
        return (config_quality_score - violations + 1) / 2
     