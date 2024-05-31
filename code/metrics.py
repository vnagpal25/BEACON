from coverage import Coverage
from duplicate_score import DuplicateScore
from user_constraints import User_Constraints


class Metric:
    def __init__(self, config_weight=0, duplicate_meal_score_weight=0, duplicate_day_score_weight=0, coverages_weight=0, constraint_weight=0):
        self.config_score_weight = config_weight
        self.duplicate_meal_score_weight = duplicate_meal_score_weight
        self.duplicate_day_score_weight = duplicate_day_score_weight
        self.coverages_weight = coverages_weight
        self.user_constraint_weight = constraint_weight

        self.score_breakdown = None
        self.rec_features = None

        self.duplicate_day_score = 0
        self.duplicate_meal_score = 0
        self.coverage_score = 0
        self.user_constraint_score = 0
        self.config_quality_score = 0

    def EvaluateMealRec(self, time_period=None, meal_plan=None, meal_configs=None, rec_constraints=None, bev_names=None, recipe_info=None, user_compatibilities=None):
        for i, day_plan in enumerate(meal_plan, 1):
            day_str = f'day {i}'
            day_plan = day_plan[day_str]

            for meal in day_plan:
                if "Beverage" in meal:
                    meal["Beverage"] = meal["Beverage"] + '_bev'

        # Checks if Meal Config is satisfied, a number between 0 and 1
        self.ConfigScoreCalc(
            meal_plan, time_period, rec_constraints)

        self.DuplicateScoreCalc(meal_plan)

        self.CoverageScoreCalc(
            meal_plan, meal_configs, bev_names, recipe_info)

        self.ConstraintsScoreCalc(
            meal_plan, user_compatibilities, recipe_info)

        score_weights = [self.config_score_weight,  self.duplicate_meal_score_weight,
                         self.duplicate_day_score_weight, self.coverages_weight,
                         self.user_constraint_weight]
        score_values = [self.config_quality_score, self.duplicate_meal_score,
                        self.duplicate_day_score,        self.coverage_score,
                        self.user_constraint_score]

        # dot product
        total_score = sum([weight * score for weight,
                          score in zip(score_weights, score_values)])

        return total_score / len(score_values), \
            self.config_quality_score, self.duplicate_meal_score,  self.duplicate_day_score, self.coverage_score, \
            self.user_constraint_score, self.score_breakdown, self.rec_features

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

                if set(inp['meal_config']).issubset(set(list(out.keys()))):
                    score += 1
                total_possible_score += 1
        self.config_quality_score = score / total_possible_score

    def DuplicateScoreCalc(self, meal_plan_):
        dup_scorer = DuplicateScore()
        self.duplicate_day_score, self.duplicate_meal_score, self.score_breakdown = dup_scorer.recommendation_score(
            meal_plan_)

    def CoverageScoreCalc(self, meal_plan_, meal_configs, bev_names, recipe_info=None):
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
                # for role, name in meal.items():
                #     if role == "Beverage":
                #         bev_index = desired_config.index('Beverage')
                #         roles_arr = [0] * len(desired_config)
                #         roles_arr[bev_index] = 1
                #     else:
                #         roles_arr = [1] * len(desired_config)
                #         if "Beverage" in meal:
                #             bev_index = desired_config.index('Beverage')
                #             roles_arr[bev_index] = 0
                #     food_items[name] = roles_arr

                for label_role, item_id in meal.items():
                    if label_role == "Beverage":
                        bev_index = desired_config.index('Beverage')
                        roles_arr = [0] * len(desired_config)
                        roles_arr[bev_index] = 1
                        food_items[item_id] = roles_arr
                    else:
                        _, _, roles = recipe_info[item_id]
                        roles_arr = [0] * len(desired_config)
                        for item_role in roles:
                            if item_role in desired_config:
                                roles_arr[desired_config.index(item_role)] = 1
                        food_items[item_id] = roles_arr

                coverage_calculator.add_food_items(food_items)
                # calculate coverage for recommended meal
                coverage_calculator.calc_coverage(meal)
                coverage_score = coverage_calculator.get_coverage()

                # append results
                day_coverages.append(
                    coverage_score if coverage_score >= 0 else 0)
                coverages.append(coverage_score if coverage_score >= 0 else 0)

            self.score_breakdown[day_str]['meal_coverages'] = day_coverages

        self.coverage_score = sum(coverages)/len(coverages)

    def ConstraintsScoreCalc(self, meal_plan_, user_compatibilities, recipes_info):
        constraint_calculator = User_Constraints()
        constraint_calculator.set_num_constraints(3)
        # User calibration
        for feature, compt in user_compatibilities.items():
            if feature == 'dairyPreference':
                constraint_calculator.add_new_constraint('hasDairy', compt)
            elif feature == 'meatPreference':
                constraint_calculator.add_new_constraint('hasMeat', compt)
            elif feature == 'nutsPreference':
                constraint_calculator.add_new_constraint('hasNuts', compt)
            else:
                print("Shouldn't be executed")

        curr_features = constraint_calculator.get_constraints()
        if 'HasDairy' in curr_features:
            constraint_calculator.remove_constraint('HasDairy')
        if 'HasMeat' in curr_features:
            constraint_calculator.remove_constraint('HasMeat')
        if 'HasNuts' in curr_features:
            constraint_calculator.remove_constraint('HasNuts')

        # take 1 day recommendations(parse all jsons) and label each one with 3 features in a spreadsheet

        # Recipe calibration
        for id, (_, features_dict, _) in recipes_info.items():
            compt_features = []
            for feature, compt in features_dict.items():
                if compt:
                    compt_features.append(feature)
            constraint_calculator.add_annotated_food_item(id, compt_features)
        features = {'hasDairy': 0, 'hasMeat': 0, 'hasNuts': 0}
        # calculate constraint scores for recommendation
        constraint_scores = []
        for i, day_plan in enumerate(meal_plan_, 1):
            day_str = f'day {i}'
            day_plan = day_plan[day_str]

            day_constraints = []
            for meal in day_plan:
                meal = meal.copy()
                del meal['Beverage']
                
                
                score, roles = constraint_calculator.calc_config(meal)
                day_constraints.append(score)
                constraint_scores.append(score)

                for role in roles:
                    features[role] += 1

            self.score_breakdown[day_str]['user_constraint_coverages'] = day_constraints

        self.user_constraint_score = sum(
            constraint_scores) / len(constraint_scores)
        self.rec_features = features
