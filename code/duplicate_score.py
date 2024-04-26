import statistics
import pprint
from collections import defaultdict

class DuplicateScore:
    def __init__(self):
      self.score_ds = {}
    
    
    def count_duplicates(self, items):
      # counts number of duplicate
      return len(items) - len(set(items))


    def day_score(self, day_plan) -> float:
        # change day score to consider duplicates within item category main course, side dish, dessert, etc.

        meal_categories = defaultdict(list) # {item_category:[item, ..., item]}
        meal_scores = []
        
        for meal in day_plan:
          meal = meal.copy()
          del meal['meal_name']
          del meal['meal_time']
          meal_scores.append(self.count_duplicates(meal.values()) / len(meal))
          for category, item in meal.items():
            meal_categories[category].append(item)
                           
        percentage_duplicates = [self.count_duplicates(category_items) / len(category_items) for category_items in meal_categories.values()]
        day_score = statistics.mean(percentage_duplicates)
        return meal_scores, day_score
   
        
    def recommendation_score(self, recommendation):
        meal_scores = []
        day_scores = []
        for i, day_plan in enumerate(recommendation, 1):
            day_str = f'day {i}'
            self.score_ds[day_str] = {}
            day_plan = day_plan[day_str]
            self.score_ds[day_str]['day_score'], self.score_ds[day_str]['meal_scores'] = \
              self.day_score(day_plan)
            meal_scores.extend(self.score_ds[day_str]['meal_scores'].values())
            day_scores.append(self.score_ds[day_str]['day_score'])
        
        # customize based off of user preference
        pprint.pp(self.score_ds)
        scores = meal_scores + day_scores
        
        # return both meal scores and day scores, aggregate based off of user preference (include in weighted sum)
        return statistics.mean(day_scores), statistics.mean(meal_scores)
      
      
# Test Cases  (implement in notebook)

# User doesn't care about duplicates

# User 