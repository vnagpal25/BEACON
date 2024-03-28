class MealConfig:
    # Holds the configuration (items) for a particular meal
    def __init__(self, config: list):
        self.config = config
    
    def has_main_course(self):
        return "Main Course" in self.config

    def has_side(self):
        return "Side" in self.config
    
    def has_dessert(self):
        return "Dessert" in self.config

    def has_beverage(self):
        return "Beverage" in self.config