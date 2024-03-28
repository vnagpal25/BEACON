class Metric:
    def __init__(self, config_weight, duplicates_weight):
        self.config_weight = config_weight
        self.duplicates_weight = duplicates_weight

    def EvaluateMealRec(self, meal_plan=None):
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
                  if good:
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
        duplicates_score = NumDuplicates(meal_plan)

        return self.config_weight * config_quality_score + self.duplicates_weight * duplicates_score
