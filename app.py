import streamlit as st
from layout_engine import create_layout
from rules import check_rules, calculate_stats
from visualizer import draw_layout

st.set_page_config(layout="wide", page_title="Building Layout Generator")
st.title("Building Layout Generator Assignment Solution")

# Help section
with st.expander("Understanding the Layouts and How It Works"):
    st.markdown("""
### How the Generator Works

The program tries different building arrangements randomly and picks the best ones.

What it does:
- Creates random building layouts with Tower A and Tower B
- Checks if they follow all the placement rules
- Gives each layout a score based on how good it is
- Shows you the highest scoring ones

Score calculation:
- More buildings equals higher score
- Larger area covered is better
- Breaking rules equals big penalty

### Reading the Visuals

What you will see:
- Black outline represents site boundary (200m x 140m)  
- Gray box represents central plaza (40m x 40m)  
- Blue boxes represent Tower A buildings (30m x 20m)  
- Green boxes represent Tower B buildings (20m x 20m)  
- Blue circles represent 60m radius (Tower A neighbor check)  
- Building labels show as A1, A2, B1, B2, etc.

### The Rules

These are the 5 rules every layout needs to follow:

1. Boundary Rule: Buildings need at least 10m space from edges (RED border if broken)
2. Spacing Rule: Buildings need 15m gap between them (RED line if too close)
3. Plaza Rule: Do not put buildings in the plaza area (RED border if overlapping)
4. Neighbor mix Rule: Every Tower A needs a Tower B within 60m (warning if violated)
5. Site Rule: Everything stays inside the site

When rules are broken:
- Thick red border means too close to edge or touching plaza
- Red line with number means buildings too close together
- Warning symbol means Tower A does not have a Tower B neighbor nearby
""")

# Sidebar controls
st.sidebar.header("Settings")
st.sidebar.markdown("Adjust these to filter what you want to see:")

min_tower_a = st.sidebar.slider("Minimum Tower A Buildings", 0, 6, 1)
min_tower_b = st.sidebar.slider("Minimum Tower B Buildings", 0, 8, 2)

# Violation filter
filter_type = st.sidebar.radio(
    "How to filter violations?",
    ["Show exactly this many", "Show up to this many"],
    index=0
)

if filter_type == "Show exactly this many":
    target_violations = st.sidebar.slider("Number of Violations", 0, 5, 0)
else:
    max_allowed_violations = st.sidebar.slider("Maximum Violations Allowed", 0, 5, 5)

min_area_sqm = st.sidebar.slider("Minimum Built Area (square meters)", 0, 10000, 1000)

how_many_iterations = st.sidebar.slider("How many layouts to try", 500, 3000, 1500, step=500)
how_many_to_show = st.sidebar.slider("How many results to display", 2, 10, 3)

st.sidebar.markdown("Note: The program makes both valid and invalid layouts. You will see red marks on the ones that break rules.")

st.sidebar.markdown("Quick Tips:")
st.sidebar.markdown("Exactly 0 violations equals only perfect layouts")
st.sidebar.markdown("Exactly 1 to 4 shows specific examples of broken rules")
st.sidebar.markdown("Up to mode shows everything from 0 to N violations")
st.sidebar.markdown("Red marks show you what is wrong")
st.sidebar.markdown("No matches? We will show you the closest ones")

# Main button
if st.button("Generate Layouts", type="primary"):
    all_results = []
    progress_bar = st.progress(0)
    status = st.empty()
    best_score_found = -999999
    valid_count = 0

    # Try generating lots of layouts
    for attempt in range(how_many_iterations):
        layout = create_layout()
        rule_checks = check_rules(layout)
        stats = calculate_stats(layout, rule_checks)

        all_results.append({
            "layout": layout,
            "rules": rule_checks,
            "stats": stats
        })

        if stats["Violations"] == 0:
            valid_count += 1

        if stats["score"] > best_score_found:
            best_score_found = stats["score"]

        progress_bar.progress((attempt + 1) / how_many_iterations)
        status.text(f"Working on it... {attempt+1}/{how_many_iterations} layouts tried | {valid_count} valid so far")

    status.empty()
    
    percentage = 100 * valid_count / how_many_iterations
    st.success(f"Done! Best score: {best_score_found:.2f} | Found {valid_count} valid layouts out of {how_many_iterations} ({percentage:.1f} percent)")

    # Filter based on user preferences
    if filter_type == "Show exactly this many":
        matching_layouts = [
            r for r in all_results
            if r["stats"]["Tower A"] >= min_tower_a
            and r["stats"]["Tower B"] >= min_tower_b
            and r["stats"]["Built Area"] >= min_area_sqm
            and r["stats"]["Violations"] == target_violations
        ]
        filter_description = f"with exactly {target_violations} violations"
    else:
        # Show everything up to max
        matching_layouts = [
            r for r in all_results
            if r["stats"]["Tower A"] >= min_tower_a
            and r["stats"]["Tower B"] >= min_tower_b
            and r["stats"]["Built Area"] >= min_area_sqm
            and r["stats"]["Violations"] <= max_allowed_violations
        ]
        filter_description = f"with 0 to {max_allowed_violations} violations"
    
    # If nothing matched, show backup results
    showing_backup = False
    if len(matching_layouts) == 0:
        st.warning(f"Could not find any layouts {filter_description}. Here are the closest ones instead...")
        showing_backup = True
        
        # Relax the requirements a bit
        matching_layouts = [
            r for r in all_results
            if r["stats"]["Tower A"] >= max(1, min_tower_a - 1)
            and r["stats"]["Tower B"] >= max(1, min_tower_b - 1)
        ]
        
        # Still nothing? Just show everything
        if len(matching_layouts) == 0:
            matching_layouts = all_results
    
    if not showing_backup:
        st.info(f"Found {len(matching_layouts)} layouts {filter_description}")
    else:
        st.info(f"Showing {min(how_many_to_show, len(matching_layouts))} layouts (could not match your exact filters)")

    if len(matching_layouts) == 0:
        st.error("Something went wrong. No layouts generated. Try running again.")
    else:
        # Sort by score, best ones first
        matching_layouts.sort(key=lambda x: x["stats"]["score"], reverse=True)

        st.markdown("---")
        if showing_backup:
            st.subheader(f"Here is What We Found (with violations explained)")
        else:
            st.subheader(f"Top {min(how_many_to_show, len(matching_layouts))} Layouts")
        
        st.markdown("Sorted by score")

        for idx in range(min(how_many_to_show, len(matching_layouts))):
            result = matching_layouts[idx]
            
            with st.container():
                st.markdown(f"### Layout Number {idx+1}")
                
                # Show key metrics
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    st.metric("Score", f"{result['stats']['score']:.1f}")
                with c2:
                    st.metric("Tower A", result['stats']['Tower A'])
                with c3:
                    st.metric("Tower B", result['stats']['Tower B'])
                with c4:
                    st.metric("Built Area", f"{result['stats']['Built Area']:,.0f} sqm")
                with c5:
                    if result['stats']['Violations'] == 0:
                        indicator = "PASS"
                    else:
                        indicator = "FAIL"
                    st.metric("Violations", f"{indicator} {result['stats']['Violations']}")
                
                # Rule status
                rule_labels = {
                    "boundary": "Boundary (at least 10m from edge)",
                    "spacing": "Spacing (at least 15m between buildings)",
                    "plaza": "Plaza (no overlap)",
                    "neighbor": "Neighbor mix (Tower A has Tower B within 60m)",
                    "site": "Site (fully inside)"
                }
                
                status_parts = []
                for k, v in result['rules'].items():
                    status = "PASS" if v else "FAIL"
                    status_parts.append(f"{rule_labels.get(k, k)}: {status}")
                
                status_text = " | ".join(status_parts)
                st.caption(status_text)
                
                # If there are violations, explain them
                if result['stats']['Violations'] > 0:
                    broken_rules = [rule_labels.get(k, k) for k, v in result['rules'].items() if not v]
                    st.warning(f"Warning: Rules broken are {', '.join(broken_rules)}")
                    
                    # Detailed breakdown
                    with st.expander("Click to see violation details"):
                        for rule_name, is_ok in result['rules'].items():
                            if not is_ok:
                                full_name = rule_labels.get(rule_name, rule_name)
                                if rule_name == "boundary":
                                    st.markdown(f"Problem with {full_name}: Some buildings are too close to the site edges (less than 10m away). Look for buildings with thick red borders.")
                                elif rule_name == "spacing":
                                    st.markdown(f"Problem with {full_name}: Some buildings are too close together (less than 15m gap). You will see red dashed lines connecting them with the distance shown.")
                                elif rule_name == "plaza":
                                    st.markdown(f"Problem with {full_name}: One or more buildings are overlapping the plaza area in the middle. They will have thick red borders.")
                                elif rule_name == "neighbor":
                                    st.markdown(f"Problem with {full_name}: Some Tower A buildings do not have any Tower B within 60m. These Tower A buildings have a warning symbol on them.")
                                elif rule_name == "site":
                                    st.markdown(f"Problem with {full_name}: Buildings are going outside the site boundaries.")
                
                # Draw it
                figure = draw_layout(result["layout"], result["stats"], result["rules"])
                st.plotly_chart(figure, use_container_width=True, key=f"layout_display_{idx}")
                
                st.markdown("---")

else:
    st.info("Click the button to start generating layouts")
    
    st.markdown("### What You Will Get:")
    st.markdown("""
    Multiple different layouts to compare
    
    Visual markers showing which rules are broken
    
    Stats on building counts and areas
    
    Filter options to find exactly what you want
    """)

    st.markdown("### Developed By:")
    st.markdown("Aditya Kumar - Intern Assignment Solution")
    st.markdown("Feel free to reach out for any questions or clarifications!")
    st.markdown("GitHub:(https://github.com/ADITYA-KUMAR-2358)")