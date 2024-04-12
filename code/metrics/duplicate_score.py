#TODO figure out meal score
#TODO in each meal there is meal name and meal time in addition to items
#deal with only items
class DuplicateScore:
    def meal_score(self, meal):
        ...


    def day_score(self, day_plan) -> float:
        # returns the percentage of meals that are duplicates
      
        # Duplicates at the day level are considered in terms of meals
        # The same meal more than once per day is a violation
        # Additionally, if all of the items in the meal have been recommended in a previous
        # meal as well, that is also a violation
        meals_set = set()
        num_violations = 0
        for meal in day_plan:
          curr_meal_set = set(meal.values())    
          if any([curr_meal_set.issubset(prev_meal) for prev_meal in meals_set]):               
            num_violations += 1
          meals_set.add(curr_meal_set)    
        
        return num_violations / len(day_plan)
    
    
    def recommendation_score(self, recommendation):
        score_ds = {}
        violations = 0
        total_chances = 0
        for i, day_plan in enumerate(recommendation, 1):
            day_str = f'day {i}'
            score_ds[day_str] = {}
            day_plan = day_plan[day_str]
            
            
            score_ds[day_str]['day_score'] = self.day_score(day_plan)
            score_ds[day_str]['meal_scores'] = {}
            
            
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
