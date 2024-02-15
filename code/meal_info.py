from meal_config import MealConfig

class MealInfo:
    # Holds information about meal
    def __init__(self, meal_name: str, meal_config: MealConfig, meal_time: str):
        self.meal_name = meal_name
        self.meal_config = meal_config
        self.meal_time = meal_time

    def write(self):
        ...