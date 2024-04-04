from coverage import Coverage

class Metric:
    def __init__(self, config_weight, duplicates_weight, coverages_weight):
        self.config_score_weight = config_weight
        self.duplicates_weight = duplicates_weight
        self.coverages_weight = coverages_weight


    def EvaluateMealRec(self, time_period=None, meal_plan=None, meal_configs=None, rec_constraints=None, bev_names=None, recipe_names=None):
        # Checks if Meal Config is satisfied, a number between 0 and 1

        config_quality_score = self.ConfigScore(meal_plan, time_period, rec_constraints)
        duplicates_score = self.NumDuplicates(meal_plan)
        coverage_score = self.CoverageScore(meal_plan, meal_configs, bev_names, recipe_names)
        return (self.config_score_weight * config_quality_score + self.duplicates_weight * duplicates_score + self.coverages_weight * coverage_score) / 3,\
                config_quality_score, duplicates_score, coverage_score


    def ConfigScore(self, meal_plan_, time_period,rec_constraints):
      score = 0
      total_possible_score = 0
      if len(meal_plan_) == time_period:
          score += 1
      total_possible_score += 1

      for i, out_day in enumerate(meal_plan_, 1):
          # Get each day's recommendations
          out_day = out_day[f'day {i}']

          for inp, out in zip(rec_constraints, out_day):
              inp = inp['meal_type']

              if inp['meal_name'] == out['meal_name']:
                  score += 1
              total_possible_score += 1

              # out.pop('meal_name')
              # out.pop('meal_time')

              if set(inp['meal_config']).issubset(set(list(out.keys()))):
                  score += 1
              total_possible_score += 1
      return score / total_possible_score


    def NumDuplicates(self, meal_plan_):
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


    def CoverageScore(self, meal_plan_, meal_configs, bev_names, recipe_names):
        coverages = []
        # iterating over whole recommendation
        for i, day_plan in enumerate(meal_plan_, 1):
          day_plan = day_plan[f'day {i}']

          # iterating over daily meal plan
          for meal in day_plan:
              coverage_calculator = Coverage()

              meal_name = meal.pop('meal_name')
              del meal['meal_time']
              
              # setting desired user request for meal config in coverage
              # calculator
              desired_config = meal_configs[meal_name].get_config()
              coverage_calculator.set_meal_config(desired_config)
              
              # setting default weights
              coverage_calculator.set_new_weights([1] * len(desired_config))

              # adding beverage role if in the recommendation
              food_items = {}
              for role, name in meal.items():
                  if role == "Beverage":
                      bev_index = desired_config.index('Beverage')
                      roles_arr = [0] * len(desired_config)
                      roles_arr[bev_index] = 1
                  else:
                      roles_arr = [1] * len(desired_config)
                      if "Beverage" in meal:
                          bev_index = desired_config.index('Beverage')
                          roles_arr[bev_index] = 0
                  food_items[name] = roles_arr
              
              coverage_calculator.add_food_items(food_items)
              # calculate coverage for recommended meal
              coverage_calculator.calc_coverage(meal)
              coverage_score = coverage_calculator.get_coverage()
              coverages.append(coverage_score)

        # TODO, return average of coverages
        return sum(coverages)/len(coverages)
