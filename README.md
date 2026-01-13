# Building Layout Generator Assignment Solution

## Overview
This program automatically generates and visualizes multiple building layouts on a 200m x 140m site, validating them against geometric placement rules. It includes both valid AND invalid layouts with clear visual indicators of violations.

## Optimization Approach
Mixed Strategy: Random Search plus Greedy Placement plus Rule Aware Positioning
- 50 percent uses optimized greedy placement (grid based, high validity rate)
- 30 percent uses aggressive placement (region based, fewer buildings, very high validity)
- 20 percent uses pure random placement (often has violations, good for examples)
- Generates 1500 layouts by default (configurable 500 to 3000)
- Each layout contains 2 to 5 Tower A and 3 to 7 Tower B buildings
- Validates all 5 placement rules for each layout
- Ranks layouts using scoring: score equals 10 times buildings plus 0.005 times area minus 200 times violations
- Displays top scoring layouts including those with violations

## Key Features

### Violation Visualization
Layouts with violations show clear visual indicators:
- RED thick borders on buildings violating boundary (less than 10m from edge) or plaza (overlapping) rules
- RED dashed lines between buildings too close (less than 15m apart) with distance labels
- Warning symbols on Tower A without Tower B neighbor within 60m
- Expandable details section to see full explanation of each violation

### Two Filter Modes

Exact number mode:
- Shows layouts with exactly N violations
- Select 0 to see only perfect layouts
- Select 1 to see layouts with exactly 1 violation
- Select 2 to 5 to see specific violation counts

Up to maximum mode:
- Shows ALL layouts from 0 to N violations
- Select 2 to see layouts with 0, 1, OR 2 violations
- Great for comparing valid versus invalid layouts side by side

### Automatic Fallback
If no layouts match your exact criteria:
- System automatically relaxes filters
- Shows best available layouts with violations
- Clearly explains which violations are present
- Helps you understand why certain combinations are difficult

## Placement Rules Validated
1. Site Rule: All buildings fully inside 200m x 140m site
2. Spacing Rule: Minimum 15m edge to edge distance between buildings
3. Boundary Rule: Minimum 10m edge to edge distance from site boundary
4. Neighbor Mix Rule: Each Tower A must have at least 1 Tower B within 60m (center to center)
5. Plaza Rule: No building overlap with 40m x 40m central plaza

## Requirements
```bash
pip install streamlit plotly
```

## How to Run
```bash
streamlit run app.py
```

The application will open in your browser at http://localhost:8501

## Usage
1. Click Generate Layouts button
2. Wait for the search to complete (progress bar shows status)
3. View layouts with violation indicators
4. Use sidebar filters to refine results:
   - Choose Exact number or Up to mode
   - Set minimum building counts
   - Set violation count preferences
   - Adjust number of layouts to display

## Understanding the Visuals

Color Coding:
- Blue rectangles represent Tower A (30m x 20m)
- Green squares represent Tower B (20m x 20m)
- Gray square represents central plaza (40m x 40m)
- Black border represents site boundary
- Red dotted line represents 10m boundary clearance zone
- Blue dashed circles represent 60m neighbor radius from Tower A

Violation Indicators (when present):
- RED thick border indicates boundary or plaza violation
- RED dashed line plus distance indicates spacing violation
- Warning symbol indicates neighbor mix violation

## Example Use Cases

View only perfect layouts:
- Filter Mode: Exact number
- Violations: 0
- Result: Only fully valid layouts

Compare valid and invalid:
- Filter Mode: Up to maximum
- Max Violations: 2
- Result: Mix of 0, 1, and 2 violation layouts

Study specific violations:
- Filter Mode: Exact number
- Violations: 1
- Result: Layouts with exactly one rule violated

No results? System shows alternatives:
- If no matches found, best available layouts displayed
- Each violation clearly explained
- Helps understand constraint difficulty

## File Structure
- app.py contains main Streamlit application with UI and optimization loop
- layout_engine.py contains random search layout generation with smart heuristics
- rules.py contains rule validation logic and scoring function
- visualizer.py contains Plotly based layout visualization

## Output
Each layout displays:
- Visual site plan with all buildings, plaza, and validation circles
- Building counts (Tower A and Tower B)
- Total built area in square meters
- Rule satisfaction status (PASS/FAIL) for all 5 rules
- Optimization score

## Features
- Interactive filtering to customize which layouts to display
- Visual rule validation with dashed circles showing neighbor mix rule compliance
- Multiple solutions to compare different layout configurations
- Real time progress showing search status during optimization
- Clear documentation with expandable help section explaining optimization and visuals

## Assignment Compliance
-Random search with scoring function (optimization approach) 
-All 5 geometric rules validated 
-Multiple layouts generated (2 or more) 
-Statistics for each layout (building counts, area, rule satisfaction) 
-Clear visual output showing site, plaza, buildings, and validation 
-Code plus instructions provided 

## Author
Aditya Kumar