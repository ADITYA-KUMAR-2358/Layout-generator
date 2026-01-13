import random
import math

# Basic measurements
SITE_WIDTH = 200
SITE_HEIGHT = 140

# Building sizes
TOWER_A_WIDTH = 30
TOWER_A_HEIGHT = 20
TOWER_B_WIDTH = 20
TOWER_B_HEIGHT = 20

# Spacing requirements
EDGE_BUFFER = 10
MIN_GAP = 15
NEIGHBOR_RANGE = 60
PLAZA_ZONE = {"x": 80, "y": 50, "w": 40, "h": 40}


def boxes_touching(box1, box2):
    """Check if two boxes overlap"""
    return not (
        box1["x"] + box1["w"] <= box2["x"] or
        box1["x"] >= box2["x"] + box2["w"] or
        box1["y"] + box1["h"] <= box2["y"] or
        box1["y"] >= box2["y"] + box2["h"]
    )


def gap_between_boxes(box1, box2):
    """Figure out how far apart two boxes are (edge to edge)"""
    horizontal_gap = max(box1["x"] - (box2["x"] + box2["w"]), box2["x"] - (box1["x"] + box1["w"]), 0)
    vertical_gap = max(box1["y"] - (box2["y"] + box2["h"]), box2["y"] - (box1["y"] + box1["h"]), 0)
    return math.sqrt(horizontal_gap * horizontal_gap + vertical_gap * vertical_gap)


def distance_between_centers(box1, box2):
    """Get distance from center to center"""
    center1_x = box1["x"] + box1["w"] / 2
    center1_y = box1["y"] + box1["h"] / 2
    center2_x = box2["x"] + box2["w"] / 2
    center2_y = box2["y"] + box2["h"] / 2
    return math.sqrt((center1_x - center2_x)**2 + (center1_y - center2_y)**2)


def spot_is_good(building, existing_ones):
    """Check if we can put a building in this spot without breaking rules"""
    # Make sure it's not too close to edges
    if not (
        building["x"] >= EDGE_BUFFER and
        building["y"] >= EDGE_BUFFER and
        building["x"] + building["w"] <= SITE_WIDTH - EDGE_BUFFER and
        building["y"] + building["h"] <= SITE_HEIGHT - EDGE_BUFFER
    ):
        return False
    
    # Don't overlap the plaza
    if boxes_touching(building, PLAZA_ZONE):
        return False
    
    # Keep distance from other buildings
    for other in existing_ones:
        if boxes_touching(building, other):
            return False
        if gap_between_boxes(building, other) < MIN_GAP:
            return False
    
    return True


def make_grid_spots(tower_type):
    """Create a bunch of possible positions in a grid pattern"""
    if tower_type == "A":
        width, height = TOWER_A_WIDTH, TOWER_A_HEIGHT
    else:
        width, height = TOWER_B_WIDTH, TOWER_B_HEIGHT
    
    possible_spots = []
    
    # Step through the site in 10m increments
    current_x = EDGE_BUFFER
    while current_x + width <= SITE_WIDTH - EDGE_BUFFER:
        current_y = EDGE_BUFFER
        while current_y + height <= SITE_HEIGHT - EDGE_BUFFER:
            possible_spots.append((current_x, current_y))
            current_y += 10
        current_x += 10
    
    # Shuffle so we don't always use the same order
    random.shuffle(possible_spots)
    return possible_spots


def try_placing_building(tower_type, buildings_so_far, attempts=200):
    """Try to find a good spot for a building"""
    if tower_type == "A":
        width, height = TOWER_A_WIDTH, TOWER_A_HEIGHT
    else:
        width, height = TOWER_B_WIDTH, TOWER_B_HEIGHT
    
    # First try the grid approach
    grid_spots = make_grid_spots(tower_type)
    
    for x_pos, y_pos in grid_spots[:100]:  # Check first 100 spots
        candidate = {
            "type": tower_type,
            "w": width,
            "h": height,
            "x": x_pos,
            "y": y_pos
        }
        
        if spot_is_good(candidate, buildings_so_far):
            return candidate
    
    # If grid didn't work, try random positions
    for _ in range(attempts):
        x_pos = random.uniform(EDGE_BUFFER, SITE_WIDTH - width - EDGE_BUFFER)
        y_pos = random.uniform(EDGE_BUFFER, SITE_HEIGHT - height - EDGE_BUFFER)
        
        candidate = {
            "type": tower_type,
            "w": width,
            "h": height,
            "x": x_pos,
            "y": y_pos
        }
        
        if spot_is_good(candidate, buildings_so_far):
            return candidate
    
    return None


def place_tower_b_near_tower_a(tower_a_building, buildings_so_far, tries=100):
    """Try to put a Tower B close to a Tower A"""
    center_x = tower_a_building["x"] + tower_a_building["w"] / 2
    center_y = tower_a_building["y"] + tower_a_building["h"] / 2
    
    # Try different distances and angles
    count = 0
    for distance in [25, 30, 35, 40, 45, 50]:
        for angle_degrees in range(0, 360, 30):  # Every 30 degrees
            if count >= tries:
                break
            
            angle_rad = math.radians(angle_degrees)
            new_x = center_x + distance * math.cos(angle_rad) - TOWER_B_WIDTH / 2
            new_y = center_y + distance * math.sin(angle_rad) - TOWER_B_HEIGHT / 2
            
            # Keep it within bounds
            new_x = max(EDGE_BUFFER, min(new_x, SITE_WIDTH - TOWER_B_WIDTH - EDGE_BUFFER))
            new_y = max(EDGE_BUFFER, min(new_y, SITE_HEIGHT - TOWER_B_HEIGHT - EDGE_BUFFER))
            
            candidate = {
                "type": "B",
                "w": TOWER_B_WIDTH,
                "h": TOWER_B_HEIGHT,
                "x": new_x,
                "y": new_y
            }
            
            # Make sure it's actually close enough
            if distance_between_centers(tower_a_building, candidate) <= NEIGHBOR_RANGE:
                if spot_is_good(candidate, buildings_so_far):
                    return candidate
            
            count += 1
    
    return None


def create_layout():
    """Main function that creates a building layout"""
    buildings = []
    
    # Decide how many of each type
    num_a = random.randint(2, 4)
    num_b = random.randint(3, 6)
    
    # Place Tower A buildings first
    tower_a_list = []
    for _ in range(num_a):
        building = try_placing_building("A", buildings, attempts=200)
        if building:
            buildings.append(building)
            tower_a_list.append(building)
    
    # Now place Tower B near each Tower A
    b_count = 0
    for tower_a in tower_a_list:
        if b_count < num_b:
            building = place_tower_b_near_tower_a(tower_a, buildings, tries=150)
            if building:
                buildings.append(building)
                b_count += 1
    
    # Add any remaining Tower B buildings
    remaining = num_b - b_count
    for _ in range(remaining):
        building = try_placing_building("B", buildings, attempts=200)
        if building:
            buildings.append(building)
    
    return buildings


def create_layout_aggressive():
    """Alternative approach - fewer buildings but more spread out"""
    buildings = []
    
    # Only place 2-3 Tower A
    num_a = random.randint(2, 3)
    
    # Split site into quadrants
    zones = [
        (20, 20, 70, 40),    # top left area
        (130, 20, 70, 40),   # top right area
        (20, 100, 70, 40),   # bottom left area
        (130, 100, 70, 40),  # bottom right area
    ]
    random.shuffle(zones)
    
    tower_a_list = []
    for i in range(min(num_a, len(zones))):
        zone = zones[i]
        for _ in range(50):
            x_pos = random.uniform(zone[0], zone[0] + zone[2] - TOWER_A_WIDTH)
            y_pos = random.uniform(zone[1], zone[1] + zone[3] - TOWER_A_HEIGHT)
            
            candidate = {
                "type": "A",
                "w": TOWER_A_WIDTH,
                "h": TOWER_A_HEIGHT,
                "x": x_pos,
                "y": y_pos
            }
            
            if spot_is_good(candidate, buildings):
                buildings.append(candidate)
                tower_a_list.append(candidate)
                break
    
    # Put a couple Tower B near each Tower A
    for tower_a in tower_a_list:
        for _ in range(2):
            building = place_tower_b_near_tower_a(tower_a, buildings, tries=100)
            if building:
                buildings.append(building)
    
    return buildings


def create_layout_random():
    """Just place buildings randomly - will probably break rules"""
    buildings = []
    
    num_a = random.randint(2, 5)
    num_b = random.randint(3, 7)
    
    # Tower A
    for _ in range(num_a):
        x_pos = random.uniform(EDGE_BUFFER, SITE_WIDTH - TOWER_A_WIDTH - EDGE_BUFFER)
        y_pos = random.uniform(EDGE_BUFFER, SITE_HEIGHT - TOWER_A_HEIGHT - EDGE_BUFFER)
        buildings.append({
            "type": "A",
            "w": TOWER_A_WIDTH,
            "h": TOWER_A_HEIGHT,
            "x": x_pos,
            "y": y_pos
        })
    
    # Tower B
    for _ in range(num_b):
        x_pos = random.uniform(EDGE_BUFFER, SITE_WIDTH - TOWER_B_WIDTH - EDGE_BUFFER)
        y_pos = random.uniform(EDGE_BUFFER, SITE_HEIGHT - TOWER_B_HEIGHT - EDGE_BUFFER)
        buildings.append({
            "type": "B",
            "w": TOWER_B_WIDTH,
            "h": TOWER_B_HEIGHT,
            "x": x_pos,
            "y": y_pos
        })
    
    return buildings


def create_layout_mixed():
    """Pick a random strategy each time"""
    choice = random.random()
    
    if choice < 0.5:
        return create_layout()
    elif choice < 0.8:
        return create_layout_aggressive()
    else:
        return create_layout_random()


# Use the mixed approach as default
create_layout = create_layout_mixed