from coverage import Coverage
from duplicate_score import DuplicateScore


class Metric:
    def __init__(self, config_weight=0, duplicate_meal_score_weight=0, duplicate_day_score_weight=0, coverages_weight=0):
        self.config_score_weight = config_weight
        self.duplicate_meal_score_weight = duplicate_meal_score_weight
        self.duplicate_day_score_weight = duplicate_day_score_weight
        self.coverages_weight = coverages_weight
        self.score_breakdown = {}

        self.duplicate_day_score = 0
        self.duplicate_meal_score = 0
        self.coverage_score = 0
        self.config_quality_score = 0

    def EvaluateMealRec(self, time_period=None, meal_plan=None, meal_configs=None, rec_constraints=None, bev_names=None, recipe_names=None):
        # Checks if Meal Config is satisfied, a number between 0 and 1
        self.ConfigScoreCalc(
            meal_plan, time_period, rec_constraints)

        self.DuplicateScoreCalc(meal_plan)

        self.CoverageScoreCalc(
            meal_plan, meal_configs, bev_names, recipe_names)

        score_weights = [self.config_score_weight,  self.duplicate_meal_score_weight,
                         self.duplicate_day_score_weight, self.coverages_weight]
        score_values = [self.config_quality_score, self.duplicate_meal_score,
                        self.duplicate_day_score,        self.coverage_score]

        # dot product
        total_score = sum([weight * score for weight,
                          score in zip(score_weights, score_values)])

        return total_score / len(score_values), \
            self.config_quality_score, self.duplicate_meal_score,  self.duplicate_day_score, self.coverage_score, \
            self.score_breakdown

    def ConfigScoreCalc(self, meal_plan_, time_period, rec_constraints):
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
        self.config_quality_score = score / total_possible_score

    def DuplicateScoreCalc(self, meal_plan_):
        dup_scorer = DuplicateScore()
        self.duplicate_day_score, self.duplicate_meal_score, self.score_breakdown = dup_scorer.recommendation_score(
            meal_plan_)

    def CoverageScoreCalc(self, meal_plan_, meal_configs, bev_names, recipe_names):
        coverages = []
        for i, day_plan in enumerate(meal_plan_, 1):
            day_str = f'day {i}'
            day_plan = day_plan[day_str]

            # iterating over daily meal plan
            day_coverages = []

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

                # append results
                day_coverages.append(
                    coverage_score if coverage_score >= 0 else 0)
                self.score_breakdown[day_str]['meal_coverages'] = day_coverages

                coverages.append(coverage_score if coverage_score >= 0 else 0)

        self.coverage_score = sum(coverages)/len(coverages)
