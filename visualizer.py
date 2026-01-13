import plotly.graph_objects as go

def draw_layout(buildings, stats, rules, show_problems=True):
    """
    Draw the building layout with Plotly
    """
    fig = go.Figure()

    # Draw the site boundary first
    fig.add_shape(
        type="rect", 
        x0=0, y0=0, x1=200, y1=140,
        line=dict(color="black", width=3),
        fillcolor="rgba(240, 240, 240, 0.3)",
        layer="below"
    )

    # Show the 10m boundary zone (red dotted)
    fig.add_shape(
        type="rect",
        x0=10, y0=10, x1=190, y1=130,
        line=dict(color="red", dash="dot", width=1),
        layer="below"
    )

    # Draw the plaza
    fig.add_shape(
        type="rect", 
        x0=80, y0=50, x1=120, y1=90,
        fillcolor="lightgrey", 
        opacity=0.7,
        line=dict(color="darkgrey", width=2, dash="dash"),
        layer="below"
    )

    # Draw circles around Tower A buildings (showing 60m range)
    for i, building in enumerate(buildings):
        if building["type"] == "A":
            center_x = building["x"] + building["w"]/2
            center_y = building["y"] + building["h"]/2
            
            fig.add_shape(
                type="circle",
                x0=center_x-60, y0=center_y-60, 
                x1=center_x+60, y1=center_y+60,
                line=dict(color="rgba(30, 144, 255, 0.4)", dash="dot", width=2),
                fillcolor="rgba(30, 144, 255, 0.05)",
                layer="below"
            )

    # Now draw the actual buildings
    for i, building in enumerate(buildings):
        # Pick colors
        if building["type"] == "A":
            fill_color = "rgba(30, 144, 255, 0.7)"
            edge_color = "darkblue"
        else:
            fill_color = "rgba(50, 205, 50, 0.7)"
            edge_color = "darkgreen"
        
        # Check if this building has problems
        edge_thickness = 2
        if show_problems and not rules.get("boundary", True):
            # Does THIS building break the boundary rule?
            if not (building["x"] >= 10 and building["y"] >= 10 and 
                   building["x"] + building["w"] <= 190 and building["y"] + building["h"] <= 130):
                edge_color = "red"
                edge_thickness = 4
        elif show_problems and not rules.get("plaza", True):
            # Does THIS building overlap the plaza?
            plaza = {"x": 80, "y": 50, "w": 40, "h": 40}
            if not (building["x"] + building["w"] <= plaza["x"] or
                   building["x"] >= plaza["x"] + plaza["w"] or
                   building["y"] + building["h"] <= plaza["y"] or
                   building["y"] >= plaza["y"] + plaza["h"]):
                edge_color = "red"
                edge_thickness = 4
        
        # Draw the building
        fig.add_shape(
            type="rect",
            x0=building["x"], y0=building["y"],
            x1=building["x"] + building["w"], y1=building["y"] + building["h"],
            fillcolor=fill_color,
            line=dict(color=edge_color, width=edge_thickness),
            layer="above"
        )

        # Add a label
        label = f"<b>{building['type']}{i+1}</b>"
        fig.add_annotation(
            x=building["x"] + building["w"]/2, 
            y=building["y"] + building["h"]/2,
            text=label,
            showarrow=False, 
            font=dict(color="white", size=11, family="Arial Black")
        )
    
    # Show violation indicators if needed
    if show_problems:
        # Spacing problems - draw red lines between buildings that are too close
        if not rules.get("spacing", True):
            import math
            for i in range(len(buildings)):
                for j in range(i+1, len(buildings)):
                    bldg1, bldg2 = buildings[i], buildings[j]
                    dx = max(bldg1["x"]-(bldg2["x"]+bldg2["w"]), bldg2["x"]-(bldg1["x"]+bldg1["w"]), 0)
                    dy = max(bldg1["y"]-(bldg2["y"]+bldg2["h"]), bldg2["y"]-(bldg1["y"]+bldg1["h"]), 0)
                    gap = math.sqrt(dx*dx + dy*dy)
                    
                    if gap < 15:
                        # Draw a line between them
                        center1_x = bldg1["x"] + bldg1["w"]/2
                        center1_y = bldg1["y"] + bldg1["h"]/2
                        center2_x = bldg2["x"] + bldg2["w"]/2
                        center2_y = bldg2["y"] + bldg2["h"]/2
                        
                        fig.add_shape(
                            type="line",
                            x0=center1_x, y0=center1_y, x1=center2_x, y1=center2_y,
                            line=dict(color="red", width=3, dash="dash")
                        )
                        
                        # Show the distance
                        fig.add_annotation(
                            x=(center1_x+center2_x)/2, y=(center1_y+center2_y)/2,
                            text=f"{gap:.1f}m",
                            showarrow=False,
                            font=dict(color="red", size=10),
                            bgcolor="white"
                        )
        
        # Neighbor problems - mark lonely Tower A buildings
        if not rules.get("neighbor", True):
            import math
            all_tower_a = [b for b in buildings if b["type"] == "A"]
            all_tower_b = [b for b in buildings if b["type"] == "B"]
            
            for tower_a in all_tower_a:
                has_buddy = False
                for tower_b in all_tower_b:
                    cx1 = tower_a["x"] + tower_a["w"]/2
                    cy1 = tower_a["y"] + tower_a["h"]/2
                    cx2 = tower_b["x"] + tower_b["w"]/2
                    cy2 = tower_b["y"] + tower_b["h"]/2
                    distance = math.sqrt((cx1-cx2)**2 + (cy1-cy2)**2)
                    if distance <= 60:
                        has_buddy = True
                        break
                
                if not has_buddy:
                    # Mark this Tower A
                    cx = tower_a["x"] + tower_a["w"]/2
                    cy = tower_a["y"] + tower_a["h"]/2
                    fig.add_annotation(
                        x=cx, y=cy,
                        text="⚠️",
                        showarrow=False,
                        font=dict(color="red", size=24)
                    )
    
    # Label the plaza
    fig.add_annotation(
        x=100, y=70,
        text="PLAZA<br>40m × 40m",
        showarrow=False,
        font=dict(color="grey", size=10, family="Arial Black")
    )

    # Add stats and rule status at the top
    rule_icons = {
        "boundary": "🏛️",
        "spacing": "↔️",
        "plaza": "🏛️",
        "neighbor": "👥",
        "site": "📐"
    }
    
    rule_info = " | ".join([
        f"{rule_icons.get(k, '•')} {k.title()}: {'✅' if v else '❌'}" 
        for k, v in rules.items()
    ])
    
    basic_stats = f"<b>Tower A:</b> {stats['Tower A']} | <b>Tower B:</b> {stats['Tower B']} | <b>Built Area:</b> {stats['Built Area']:,.0f} m²"
    
    fig.add_annotation(
        x=100, y=148,
        text=basic_stats,
        showarrow=False,
        font=dict(size=12, color="black"),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="black",
        borderwidth=1,
        xref="x",
        yref="y"
    )
    
    fig.add_annotation(
        x=100, y=142,
        text=rule_info,
        showarrow=False,
        font=dict(size=10, color="darkblue"),
        xref="x",
        yref="y"
    )

    # Configure the layout
    fig.update_layout(
        xaxis=dict(
            range=[-5, 205],
            title="Distance (m)",
            showgrid=True,
            gridcolor="lightgrey",
            dtick=20,
            zeroline=False
        ),
        yaxis=dict(
            range=[-5, 152],
            title="Distance (m)",
            showgrid=True,
            gridcolor="lightgrey",
            dtick=20,
            scaleanchor="x",
            scaleratio=1,
            zeroline=False
        ),
        height=650,
        width=900,
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig