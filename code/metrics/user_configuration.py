import warnings


class User_Constraints:

    # Define the user configuration (e.g., HasDairy, HasMeat, HasNuts)
    constraints = {
        "HasDairy": 0,
        "HasMeat": 0,
        "HasNuts": 0,
    }  # -1: No, 0: Neutral, 1: Yes

    # Default number of user-defined constraints
    num_constraints = 3  # HasDairy, HasMeat, HasNuts

    # Annotated food items
    food_items = {}

    # Calculate the configuration score
    config_score = 0

    def __init__(self):
        print("Class initiated")

    def set_num_constraints(self, num_constraints: int):
        """Define the number of user-defined constraints.

        Args:
            num_constraints (int): Number of user-defined constraints.
        """
        self.num_constraints = num_constraints

    def get_num_constraints(self):
        """Return the number of user-defined constraints."""
        return self.num_constraints

    def define_constraints(self, constraints: list):
        """Define the user configuration.

        Args:
            constraints (list): List of user-defined constraints.
        """
        if len(constraints) != self.num_constraints:
            raise Exception(
                "Number of constraints must match the number of user-defined constraints."
            )
        self.constraints = constraints

    def get_constraints(self):
        """Return user configuration."""
        return self.constraints

    def add_annotated_food_items(self, annotated_food: dict):
        """Annotate food items with dairy, meat, or nuts.

        Args:
            annotated_food (dict): Dictionary mapping food items to their corresponding roles. If using default configuration, the annotated food items should be in the form of 'food_item': ['HasDairy', 'HasMeat', 'HasNuts'].

        """
        for i in annotated_food:
            if any(role not in self.constraints for role in annotated_food[i]):
                warnings.warn(
                    "Annotated food items contain possibly new constraints that are not defined in the current configuration."
                )
            self.food_items[i] = annotated_food[i]

    def get_annotated_food_items(self):
        """Return annotated food items."""
        return self.food_items
