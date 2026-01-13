import math

# Site specs
PLAZA_AREA = {"x": 80, "y": 50, "w": 40, "h": 40}
EDGE_CLEARANCE = 10
BUILDING_GAP = 15
NEIGHBOR_DIST = 60
SITE_WIDTH = 200
SITE_HEIGHT = 140


def shapes_overlap(shape1, shape2):
    """Check if two rectangles are touching or overlapping"""
    return not (
        shape1["x"] + shape1["w"] <= shape2["x"] or
        shape1["x"] >= shape2["x"] + shape2["w"] or
        shape1["y"] + shape1["h"] <= shape2["y"] or
        shape1["y"] >= shape2["y"] + shape2["h"]
    )


def measure_gap(shape1, shape2):
    """Measure the gap between two rectangles (edge to edge)"""
    x_gap = max(shape1["x"] - (shape2["x"] + shape2["w"]), shape2["x"] - (shape1["x"] + shape1["w"]), 0)
    y_gap = max(shape1["y"] - (shape2["y"] + shape2["h"]), shape2["y"] - (shape1["y"] + shape1["h"]), 0)
    return math.sqrt(x_gap * x_gap + y_gap * y_gap)


def center_to_center_dist(shape1, shape2):
    """Get the distance between the centers of two rectangles"""
    center1_x = shape1["x"] + shape1["w"] / 2
    center1_y = shape1["y"] + shape1["h"] / 2
    center2_x = shape2["x"] + shape2["w"] / 2
    center2_y = shape2["y"] + shape2["h"] / 2
    
    return math.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)


def check_rules(buildings):
    """
    Check if the layout follows all the placement rules
    
    Returns a dict with True/False for each rule
    """
    results = {
        "site": True,
        "boundary": True,
        "spacing": True,
        "plaza": True,
        "neighbor": True
    }

    # Check each building
    for building in buildings:
        # Is it inside the site?
        if not (
            building["x"] >= 0 and
            building["y"] >= 0 and
            building["x"] + building["w"] <= SITE_WIDTH and
            building["y"] + building["h"] <= SITE_HEIGHT
        ):
            results["site"] = False
            break
    
    # Are buildings far enough from edges?
    for building in buildings:
        if not (
            building["x"] >= EDGE_CLEARANCE and
            building["y"] >= EDGE_CLEARANCE and
            building["x"] + building["w"] <= SITE_WIDTH - EDGE_CLEARANCE and
            building["y"] + building["h"] <= SITE_HEIGHT - EDGE_CLEARANCE
        ):
            results["boundary"] = False
            break

    # Check plaza - no overlaps allowed
    for building in buildings:
        if shapes_overlap(building, PLAZA_AREA):
            results["plaza"] = False
            break

    # Check spacing between buildings
    for i in range(len(buildings)):
        for j in range(i + 1, len(buildings)):
            # Overlapping?
            if shapes_overlap(buildings[i], buildings[j]):
                results["spacing"] = False
                break
            
            # Too close?
            gap = measure_gap(buildings[i], buildings[j])
            if gap < BUILDING_GAP - 0.01:  # tiny tolerance for rounding
                results["spacing"] = False
                break
        
        if not results["spacing"]:
            break

    # Neighbor rule - every Tower A needs a Tower B friend nearby
    tower_a_buildings = [b for b in buildings if b["type"] == "A"]
    tower_b_buildings = [b for b in buildings if b["type"] == "B"]

    for tower_a in tower_a_buildings:
        found_neighbor = False
        for tower_b in tower_b_buildings:
            if center_to_center_dist(tower_a, tower_b) <= NEIGHBOR_DIST + 0.01:
                found_neighbor = True
                break
        
        if not found_neighbor:
            results["neighbor"] = False
            break

    return results


def calculate_stats(buildings, rule_results):
    """
    Figure out the stats for this layout
    """
    count_a = sum(1 for b in buildings if b["type"] == "A")
    count_b = sum(1 for b in buildings if b["type"] == "B")
    total_area = sum(b["w"] * b["h"] for b in buildings)
    
    # How many rules are broken?
    violations = sum(1 for v in rule_results.values() if v == False)
    
    # Calculate a score
    # More buildings = good
    # More area = good
    # Violations = very bad
    score = (10 * (count_a + count_b)) + (0.005 * total_area) - (200 * violations)
    
    return {
        "Tower A": count_a,
        "Tower B": count_b,
        "Built Area": round(total_area, 2),
        "Violations": violations,
        "score": round(score, 2)
    }