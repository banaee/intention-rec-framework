# file movement_probability.py
# standalone script including functions for calculating movement probabilities for targets 
# in the environment based on human movement and target positions
# This script is part of the intentions module and is designed to be used in conjunction with a model of the environment




def calculate_movement_direction(position_history, human_id):
    """Calculate the movement direction vector from position history"""
    if len(position_history[human_id]) >= 2:
        prev_pos = position_history[human_id][-2][1]
        curr_pos = position_history[human_id][-1][1]
        
        dx = curr_pos[0] - prev_pos[0]
        dy = curr_pos[1] - prev_pos[1]
        
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            return (dx/length, dy/length)
    return None


def calculate_target_probabilities(model, human_id, human_pos, movement_dir=None):
    """
    Calculate probabilities for movement targets
    
    This is the main method for target probability calculation.
    Implementation can be replaced with different approaches:
    - Simple distance/trajectory approach (current implementation)
    - Bayesian inference approach
    - Machine learning approach
    - etc.
    """
    # Current implementation uses trajectory-based calculation
    # Could be replaced with Bayesian or other approaches
    
    target_probabilities = {}
    
    if movement_dir:
        # Get trajectory-based probabilities
        target_probabilities = calculate_trajectory_based_probabilities(model=model,
                                                                        human_id=human_id,
                                                                        human_pos=human_pos,
                                                                        movement_dir=movement_dir)
    
    if not target_probabilities:
        # Fallback to distance-based probabilities
        target_probabilities = calculate_distance_based_probabilities(
            model, human_id, human_pos)
    
    if not target_probabilities:
        # Final fallback to uniform distribution
        target_probabilities = get_uniform_target_probabilities(model)
    
    return target_probabilities



def calculate_trajectory_based_probabilities(model, human_id, human_pos, movement_dir):
    """Calculate target probabilities based on movement trajectory"""
    potential_targets = []
    target_probabilities = {}
    
    # Check each item
    for item_id, item in model.items.items():
        score, dist = score_target_by_trajectory(human_pos, item.pos, movement_dir)
        if score > 0:
            potential_targets.append((item_id, score, dist))
    
    # Check kitting table
    kt = model.kitting_table
    score, dist = score_target_by_trajectory(human_pos, kt.pos, movement_dir)
    if score > 0:
        potential_targets.append(("kitting_table", score, dist))
    
    # Convert scores to probabilities
    if potential_targets:
        # Sort by score
        potential_targets.sort(key=lambda x: x[1], reverse=True)
        
        # Get scores only
        scores = [t[1] for t in potential_targets]
        
        # Convert to probabilities
        total_score = sum(scores)
        if total_score > 0:
            for target, score, dist in potential_targets:
                prob = score / total_score
                target_probabilities[target] = prob
                print(f"Target {target}: probability {prob:.2f}, distance {dist:.1f}")
    
    return target_probabilities




def score_target_by_trajectory(human_pos, target_pos, movement_dir):
    """Score a target based on alignment with movement trajectory and distance"""
    # Vector from human to target
    to_target = (target_pos[0] - human_pos[0], target_pos[1] - human_pos[1])
    dist = (to_target[0]**2 + to_target[1]**2)**0.5
    
    # Max distance to consider
    max_dist = 300
    
    # Calculate dot product to see if target is in front of human
    dot_product = movement_dir[0] * to_target[0] + movement_dir[1] * to_target[1]
    
    # If target is in front and within reasonable distance
    if dot_product > 0 and dist < max_dist:
        # Calculate a score based on alignment and distance
        alignment = dot_product / dist  # Higher when directly in front
        score = alignment * (1 - dist/max_dist)  # Higher for closer items
        return score, dist
    
    return 0, dist


def calculate_distance_based_probabilities(model, human_id, human_pos):
    """Calculate target probabilities based on distance only"""
    target_probabilities = {}
    max_dist = 300  # Maximum distance to consider
    
    # Calculate inverse distances (closer = higher score)
    total_inv_dist = 0
    for item_id, item in model.items.items():
        dist = calculate_distance(human_pos, item.pos)
        if dist < max_dist:
            inv_dist = 1 / (dist + 1)  # Add 1 to avoid division by zero
            total_inv_dist += inv_dist
            target_probabilities[item_id] = inv_dist
    
    # Add kitting table
    kt_dist = calculate_distance(human_pos, model.kitting_table.pos)
    if kt_dist < max_dist:
        inv_dist = 1 / (kt_dist + 1)
        total_inv_dist += inv_dist
        target_probabilities["kitting_table"] = inv_dist
    
    # Normalize probabilities if we found any targets
    if total_inv_dist > 0:
        for target in target_probabilities:
            target_probabilities[target] /= total_inv_dist
    
    return target_probabilities



    
def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions"""
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5



def calculate_bayesian_target_probabilities(model, human_id, human_pos, movement_dir=None):
    """
    Calculate target probabilities using Bayesian inference
    P(target|observation) ∝ P(observation|target) * P(target)
    """
    # Get prior probabilities (could be from previous step or task context)
    prior_probs = get_target_priors(model, human_id)
    
    # Calculate likelihood for each target given the observation
    likelihoods = {}
    for target_id in get_all_possible_targets(model):
        likelihoods[target_id] = calculate_target_likelihood(model, target_id, human_pos, movement_dir)
    
    # Apply Bayes rule
    posterior_probs = {}
    total_probability = 0
    for target_id, prior in prior_probs.items():
        posterior = likelihoods[target_id] * prior
        posterior_probs[target_id] = posterior
        total_probability += posterior
    
    # Normalize
    if total_probability > 0:
        for target_id in posterior_probs:
            posterior_probs[target_id] /= total_probability
    
    return posterior_probs


def get_target_priors(model, human_id):
    """Get prior probabilities for targets based on previous observations"""
    # For now, use uniform priors
    return get_uniform_target_probabilities(model)



def get_all_possible_targets(model):
    """Get list of all possible targets in the environment"""
    targets = list(model.items.keys())
    targets.append("kitting_table")
    return targets



def get_uniform_target_probabilities(model):
    """Return uniform probability distribution over all possible targets"""
    target_probabilities = {}
    uniform_prob = 1.0 / (len(model.items) + 1)  # +1 for kitting table
    
    for item_id in model.items:
        target_probabilities[item_id] = uniform_prob
    target_probabilities["kitting_table"] = uniform_prob
    
    return target_probabilities


def calculate_target_likelihood(model, target_id, human_pos, movement_dir):
    """Calculate likelihood of observing movement given a target"""
    if not movement_dir:
        return 0.1  # Default likelihood when no movement
    
    # Get target position
    target_pos = None
    if target_id == "kitting_table":
        target_pos = model.kitting_table.pos
    elif target_id in model.items:
        target_pos = model.items[target_id].pos
    else:
        return 0.05  # Unknown target
    
    # Calculate likelihood based on alignment
    _, dist = score_target_by_trajectory(human_pos, target_pos, movement_dir)
    if dist > 300:
        return 0.05  # Too far
    
    # Simplified likelihood based on score
    score, _ = score_target_by_trajectory(human_pos, target_pos, movement_dir)
    return max(0.1, score * 5)  # Scale up for better contrast


