import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple
import math
import tempfile
import webbrowser
import os

USE_PIXEL_METRICS = True;
PIXEL_SIZE = 10;
LAYER_HEIGHT = 5;
RATIO = 0.7071;
X_SIZE = 2.5;
Y_SIZE = 2.5;
Z_SIZE = 2.5;
WIRE_LENGTH = 0;
ADDED_WIRE = 0;
TOTAL_LENGTH = 0;
LAST_VERTICAL_LAYER = 0;

class HTree3D:
    """
    A 3D H-tree visualizer using Plotly.
    
    An H-tree is a fractal tree structure where each node has an H-shape,
    and each branch recursively contains smaller H-shapes.
    """
    
    def __init__(self, scale_factor: float = 0.7937):
        self.lines = []  # Store all line segments as (x1,y1,z1, x2,y2,z2, layer)
        self.points = []  # Store all points for reference
        self.colors = ['red', 'orange', 'green']  # Color cycle
        self.scale_factor = scale_factor  # Scale factor for H-tree arms
        self.is_dimensional = USE_PIXEL_METRICS;

    def gen_configurable_htree(self, center: Tuple[float, float, float], size: float, blueprint: str) -> None:
        """
        Generate a configurable H-tree based on a blueprint string.
        """
        # Parse the blueprint string
        levels = len(blueprint)

        if levels <= 0:
            return
        
        self._compute_path_length(size, blueprint)

        self._configurable_generate_level(center, size, blueprint, 0)
        
        # Now that we know the input is valid, let's build something cool.

    def _compute_path_length(self, size: float = 2.0, blueprint: str = ""):
        global WIRE_LENGTH;
        global LAYER_HEIGHT;
        global RATIO;
        global ADDED_WIRE;
        global TOTAL_LENGTH;
        factor = 1;
        x = set('0xX');
        y = set('1yY');
        z = set('2zZ');
        for ch in blueprint:
            if ch in z:
                ADDED_WIRE += LAYER_HEIGHT;
                WIRE_LENGTH += LAYER_HEIGHT;
                TOTAL_LENGTH += LAYER_HEIGHT * 2 * factor;
            else:
                WIRE_LENGTH += size/2; # Because we're always going to branch to one half or the other
                size *= RATIO;
                TOTAL_LENGTH += size * factor
            factor *= 2;


    def _configurable_generate_level(self,center, size, blueprint, layer) -> None:
        """Recursive structure for building abritrarily oriented (but legal) 3d htrees
        each layer passes a 1-shorter slice of instructions to the next set of levels.
        """
        global LAYER_HEIGHT
        global LAST_VERTICAL_LAYER
        if blueprint == "":
            return
        
        
        if self.is_dimensional:
            next_size = size * RATIO
        elif len(blueprint) >= 3:
            if (blueprint[2] == blueprint[0]):
                next_size = size * 0.7071 
            else:
                next_size = size * 0.7937
        else:
            next_size = size * self.scale_factor

        if len(blueprint) == 1:
            add_nodes = 0
        else:
            add_nodes = layer + 1
        x, y, z = center
        half_size = size * 0.5
        
        orientation = blueprint[0]
        if orientation == '0': ### X DIRECTION ###
            sub_side = (x, y-half_size, z)
            pos_side = (x, y+half_size, z)

        elif orientation == '1': ### Y DIRECTION ###
            sub_side = (x - half_size, y, z)
            pos_side = (x + half_size, y, z)
        elif orientation == '2': ### Z DIRECTION ###
            if not self.is_dimensional:
                sub_side = (x, y, z - half_size)
                pos_side = (x, y, z + half_size)
            else:
                if layer == LAST_VERTICAL_LAYER:
                    #print("Amending height for layer: " + str(layer))
                    sub_side = (x, y, z - LAYER_HEIGHT)
                    pos_side = (x, y, z)
                    next_size = size
                else:
                    sub_side = (x, y, z - LAYER_HEIGHT*(2**(blueprint.count("2")-2)))
                    pos_side = (x, y, z + LAYER_HEIGHT*(2**(blueprint.count("2")-2)))
                    next_size = size

        ### Let's Make Some Recursive Calls! ###

        self.add_line(sub_side,pos_side, layer, add_nodes)
        self._configurable_generate_level(sub_side, next_size, blueprint[1:], layer+1)
        self._configurable_generate_level(pos_side, next_size, blueprint[1:], layer+1)

    def add_line(self, point1: Tuple[float, float, float], 
                 point2: Tuple[float, float, float], layer: int, max_layers: int) -> None:
        """Add a line segment to the tree."""
        self.lines.append((*point1, *point2, layer))
        # Store points with their associated layer for size scaling
        if layer < max_layers:
            self.points.extend([(point1, layer), (point2, layer)])

    def create_plotly_figure(self, title: str = "3D H-Tree Visualization", 
                           isometric: bool = False) -> go.Figure:
        """
        Create a Plotly 3D figure from the generated H-tree.
        
        Returns:
            Plotly Figure object with interactive 3D visualization
        """
        if not self.lines:
            raise ValueError("No H-tree generated. Call generate_htree() first.")
        
        # Create the 3D line plot
        fig = go.Figure()
        
        # Group lines by orientation for color coding
        # Red for X-direction, Orange for Y-direction, Green for Z-direction
        orientation_colors = {
            'x': 'red',
            'y': 'orange', 
            'z': 'green'
        }
        
        # Group lines by both orientation and layer for individual control
        lines_by_orientation_and_layer = {}
        
        for line in self.lines:
            x1, y1, z1, x2, y2, z2, layer = line
            
            # Determine orientation by checking which coordinate varies
            if abs(x1 - x2) > 1e-10:  # Line varies in X dimension
                orientation = 'x'
            elif abs(y1 - y2) > 1e-10:  # Line varies in Y dimension
                orientation = 'y'
            elif abs(z1 - z2) > 1e-10:  # Line varies in Z dimension
                orientation = 'z'
            else:
                continue  # Skip degenerate lines (shouldn't happen)
            
            key = (orientation, layer)
            if key not in lines_by_orientation_and_layer:
                lines_by_orientation_and_layer[key] = []
            lines_by_orientation_and_layer[key].append((x1, y1, z1, x2, y2, z2))
        
        # Add traces for each orientation/layer combination
        orientation_names = {'x': 'X', 'y': 'Y', 'z': 'Z'}
        
        # Sort by layer first, then by orientation to preserve layer order
        for (orientation, layer), lines in sorted(lines_by_orientation_and_layer.items(), key=lambda x: (x[0][1], x[0][0])):
            x_lines, y_lines, z_lines = [], [], []
            
            for line_data in lines:
                x1, y1, z1, x2, y2, z2 = line_data
                x_lines.extend([x1, x2, None])  # None creates breaks between lines
                y_lines.extend([y1, y2, None])
                z_lines.extend([z1, z2, None])
            
            # Use consistent line width for all orientations
            base_width = 12
            color = orientation_colors[orientation]
            
            fig.add_trace(go.Scatter3d(
                x=x_lines,
                y=y_lines,
                z=z_lines,
                mode='lines',
                line=dict(
                    color=color,
                    width=max(base_width*(0.75**(layer-1)),1)
                ),
                name=f'Layer {layer} ({orientation_names[orientation]})',
                hoverinfo='skip'
            ))
        
        all_points = list(set(self.points))
        if all_points:
            # Collect all junction points and their sizes/colors for a single trace
            all_x_points = []
            all_y_points = []
            all_z_points = []
            all_sizes = []
            all_colors = []
            
            # Create a mapping from junction points to the orientation of the line they sit at the center of
            junction_center_orientations = {}
            for line in self.lines:
                x1, y1, z1, x2, y2, z2, layer = line
                
                # Determine line orientation
                if abs(x1 - x2) > 1e-10:
                    orientation = 'x'
                elif abs(y1 - y2) > 1e-10:
                    orientation = 'y'
                elif abs(z1 - z2) > 1e-10:
                    orientation = 'z'
                else:
                    continue
                
                # Calculate the midpoint of this line
                midpoint = ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)
                midpoint_key = (round(midpoint[0], 10), round(midpoint[1], 10), round(midpoint[2], 10))
                
                # Map this midpoint to the orientation of the line it's the center of
                junction_center_orientations[midpoint_key] = orientation
            
            # Group points by layer and calculate sizes
            points_by_layer = {}
            for point_data in all_points:
                point, layer = point_data
                if layer not in points_by_layer:
                    points_by_layer[layer] = []
                points_by_layer[layer].append(point)
            
            base_size = 12  # Starting size for level 1 junctions
            
            # Add special origin junction at (0,0,0) first so it renders with proper depth
            all_x_points.append(0)
            all_y_points.append(0)
            all_z_points.append(0)
            all_sizes.append(base_size)
            all_colors.append('white')
            
            # Collect all points into single arrays for one trace
            for layer in sorted(points_by_layer.keys()):
                points = points_by_layer[layer]
                
                # Calculate junction size: scale with line width
                junction_size = base_size * (0.85 ** (layer - 1))  # Same scaling as line width

                
                # Add to combined arrays
                for point in points:
                    point_key = (round(point[0], 10), round(point[1], 10), round(point[2], 10))
                    
                    # Determine junction color based on the line it sits at the center of
                    if point_key in junction_center_orientations:
                        orientation = junction_center_orientations[point_key]
                        color = orientation_colors[orientation]
                    else:
                        color = 'white'  # Fallback for points not at center of any line
                                                
                    all_x_points.append(point[0])
                    all_y_points.append(point[1])
                    all_z_points.append(point[2])
                    all_sizes.append(junction_size)
                    all_colors.append(color)
            
            # Add all junctions (including origin) as a single trace
            fig.add_trace(go.Scatter3d(
                x=all_x_points,
                y=all_y_points,
                z=all_z_points,
                mode='markers',
                marker=dict(
                    size=all_sizes,
                    color=all_colors,
                    opacity=0.8,
                    line=dict(width=0)  # Remove white outline
                ),
                name='Junctions',
                hoverinfo='x+y+z'
            ))
        
        # Update layout for better visualization
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='white')
            ),
            scene=dict(
                xaxis=dict(
                    title=dict(text='X', font=dict(color='white')), 
                    range=[-X_SIZE, X_SIZE],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title=dict(text='Y', font=dict(color='white')), 
                    range=[-Y_SIZE, Y_SIZE],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                zaxis=dict(
                    title=dict(text='Z', font=dict(color='white')), 
                    range=[-Z_SIZE, Z_SIZE],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                camera=dict(
                    projection=dict(type="orthographic" if isometric else "perspective"),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'  # Keeps proportions correct
            ),
            paper_bgcolor='black',  # Overall background
            plot_bgcolor='black',   # Plot area background
            font=dict(color='white'),  # All text white
            width=1200,
            height=900,
            showlegend=True,
            legend=dict(
                font=dict(color='white'),
                bgcolor='rgba(0, 0, 0, 0.5)',  # Semi-transparent legend background
                bordercolor='rgb(120, 120, 120)',
                borderwidth=1
            )
        )
        
        return fig

def visualize_custom_htree(size: float = 2.0, scale_factor: float = 0.7937, isometric: bool = False, blueprint: str = "") -> go.Figure:
    htree = HTree3D(scale_factor=scale_factor)
    global LAST_VERTICAL_LAYER
    for i in range(len(blueprint)):
        if blueprint[i] == "2":
            LAST_VERTICAL_LAYER = i;
    htree.gen_configurable_htree((0,0,0), size, blueprint)  # Don't assign the return value

    projection_type = "Isometric" if isometric else "Perspective"
    title = f"3D H-Tree with {len(blueprint)} levels ({projection_type}, scale: {scale_factor:.4f})"
    return htree.create_plotly_figure(title, isometric)

def show_with_dark_background(fig: go.Figure):
    html_content = fig.to_html(include_plotlyjs='cdn')
    
    # Inject dark background CSS
    dark_css = """
    <style>
        body { 
            background-color: black !important; 
            margin: 0; 
            padding: 20px; 
            font-family: Arial, sans-serif;
        }
        .plotly-graph-div { 
            margin: 0 auto; 
            display: block; 
        }
    </style>
    """

    html_content = html_content.replace('<head>', '<head>' + dark_css)
    
    # Save to a temporary file and open it
    with tempfile.NamedTemporaryFile(mode='w', suffix='_dark_htree.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name
    
    # Open the dark-themed version in browser
    webbrowser.open(f'file://{temp_path}')

def main():

    print("3D H-Tree Visualizer")
    print("===================")

    generate_style = input("Select your tree generation type (1 = configurable, 0 = cubioid, default = 0) ").strip()
    
    if generate_style == "1":
        print("\nDefine your Htree as a no-space string, starting from the core dimension.")
        print("0,x,X = x-dimension")
        print("1,y,Y = y-dimension")
        print("2,z,Z = z-dimension")
        while True:
            try:
                input_blueprint = input("Enter htree as a no-space string: ").strip()
                levels = len(input_blueprint)
                standardized_blueprint = ""
                for ch in input_blueprint:
                    if ch in set("0xX"):
                        standardized_blueprint += "1"
                    elif ch in set("1yY"):
                        standardized_blueprint += "0"
                    elif ch in set("2zZ"):
                        standardized_blueprint += "2"
                    else:
                        raise ValueError("At least one value is invalid. The only acceptable characters are 0,1,2,x,y,z,X,Y,Z.")
                        
                for i, char in enumerate(standardized_blueprint):
                    if i > 0 and char == standardized_blueprint[i - 1]:
                        raise ValueError(f"Character '{char}' is repeated immediately at position {i}. No immediate repeats allowed.")
                break
            except ValueError as e:
                print(e)
        final_blueprint = standardized_blueprint
    else:
        while True:
            try:
                levels = input("Enter number of levels (1-21, default=6): ").strip()
                if levels == "":
                    levels = 6
                else:
                    levels = int(levels)
                
                if 1 <= levels <= 21:
                    break
                else:
                    print("Please enter a number between 1 and 21.")
            except ValueError:
                print("Please enter a valid number.")
    
    scale_factor = 1
    print("\nChoose projection type:")
    print("1. Isometric")
    print("2. Perspective")
    
    while True:
        try:
            projection_choice = input("Enter choice (1-2, default=1): ").strip()
            if projection_choice == "2":
                isometric = False
                break
            else:
                isometric = True
                break
        except ValueError:
            print("Please enter a valid number.")

    projection_type = "Isometric" if isometric else "Perspective"
    print(f"\nGenerating 3D H-tree with {levels} levels in {projection_type.lower()} projection.")
    
    if generate_style != "1":
        final_blueprint = ""
        for i in range(levels):
            final_blueprint += str(i % 3)
    
    computed_size = 2
    if USE_PIXEL_METRICS:
        # Compute the size to build off of!
        computed_size = PIXEL_SIZE/(RATIO**len(final_blueprint))
    global X_SIZE
    print("Computed Size = " + str(computed_size) +"")
    X_SIZE = computed_size;
    global Y_SIZE
    Y_SIZE = computed_size;
    global Z_SIZE
    Z_SIZE = computed_size;

    fig = visualize_custom_htree(size=computed_size, scale_factor=scale_factor, isometric=isometric, blueprint=final_blueprint)

    print("Opening interactive 3D visualization...")

    show_with_dark_background(fig)

    print("Wire length excluding intentional delay: {:.2f}".format(WIRE_LENGTH) + "um")
    print("Added intentional delay: {:.2f}".format(ADDED_WIRE) + "um")
    print("Total wire length: {:.2f}".format(ADDED_WIRE + WIRE_LENGTH) + "um")
    print("Average segment length: " + str(TOTAL_LENGTH/(2**(len(final_blueprint)+1) - 2)) + "um")
        
    save_html = input("\nSave as HTML file? (y/n, default=n): ").strip().lower()
    if save_html in ['y', 'yes']:
        projection_suffix = "_isometric" if isometric else "_perspective"
        filename = f"htree_3d_{levels}_levels{projection_suffix}.html"
        fig.write_html(filename)
        print(f"Saved as {filename}")

if __name__ == "__main__":
    main()