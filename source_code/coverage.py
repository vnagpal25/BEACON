def calc_coverage(meal, recommendation):
    """
    Given a meal (meal[]) and a recommended set of foods (recommendation[]), 
    check how many roles required for a meal are satisfied by the recommended foods.
    Penalize both excess and lower roles than the ideal weight number.
    """
    # Define the ideal weight for each role in a meal
    ideal_weights = [1, 1, 1, 1]  # Default ideal weights for each role

    # Data augmentation: Define roles each food can take
    food_roles = {
        'omelet': [0, 1, 1, 0],  # Example: omelet can be a main course and a side dish
        'salad': [0, 1, 1, 0],
        'cake':[0, 0, 0, 1],
        'tea':[1, 0, 0, 0]
        # Add more foods and their roles here
    }

    # Initialize coverage and excess variables for each role
    coverage = [0, 0, 0, 0]
    excess = [0, 0, 0, 0]

    # Calculate coverage and excess for each recommended food
    for food in recommendation:
        if food in food_roles:
            roles = food_roles[food]
            for i in range(len(roles)):
                if roles[i] == 1:
                    coverage[i] += 1
                else:
                    excess[i] += 1

    # Calculate the total coverage score
    total_coverage_score = 0
    for i in range(len(meal)):
        shortfall = max(0, ideal_weights[i] - coverage[i])  # Penalties for shortfall (how many roles are still left unfulfilled?)
        excess_penalty = excess[i] * 0.5  # Penalize excess roles (how many roles have excess food items recommended?)
        total_coverage_score += max(0, coverage[i] - excess_penalty - shortfall)

    # Normalize the coverage score
    max_possible_score = sum(ideal_weights)
    min_possible_score = 0  # When no roles are satisfied
    normalized_score = (total_coverage_score - min_possible_score) / \
        (max_possible_score - min_possible_score)

    return normalized_score

# Example usage:
meal = ['beverage', 'main course', 'side dish', 'dessert']

recommendation = {'main course': 'omelet', 'side dish': 'salad', 'dessert': 'cake'}
recommendation = ['omelet', 'salad', 'cake']  # Example recommendation

coverage_score = calc_coverage(meal, recommendation)
print("Coverage score:", coverage_score)
