import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple
import math
import tempfile
import webbrowser
import os

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

    def gen_configurable_htree(self, center: Tuple[float, float, float], size: float, blueprint: str) -> None:
        """
        Generate a configurable H-tree based on a blueprint string.
        """
        # Parse the blueprint string
        levels = len(blueprint)

        if levels <= 0:
            return
        
        self._configurable_generate_level(center, size, blueprint, 0)
        
        # Now that we know the input is valid, let's build something cool.

    def generate_htree(self, center: Tuple[float, float, float], 
                      size: float, levels: int, 
                      orientation: str = 'xy') -> None:
        """
        Generate a 3D H-tree level by level.
        
        Level 1: Center line
        Level 2: Perpendicular lines (making first H)
        Level 3+: Lines at the endpoints, continuing the pattern
        
        Args:
            center: (x, y, z) center point
            size: Length of the H arms
            levels: Total number of levels to generate
            orientation: 'xy', 'xz', or 'yz' - which plane the lines lie in
        """
        if levels <= 0:
            return
            
        # Generate all levels progressively
        self._generate_level_recursive(center, size, levels, orientation, 1)
    
    def _configurable_generate_level(self,center, size, blueprint, layer) -> None:
        """Recursive structure for building abritrarily oriented (but legal) 3d htrees
        each layer passes a 1-shorter slice of instructions to the next set of levels.
        """
        if blueprint == "":
            return
        
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
            #self.add_line((x, y - half_size, z), (x, y + half_size, z), layer, add_nodes)
        elif orientation == '1': ### Y DIRECTION ###
            sub_side = (x - half_size, y, z)
            pos_side = (x + half_size, y, z)
        elif orientation == '2': ### Z DIRECTION ###
            sub_side = (x, y, z - half_size)
            pos_side = (x, y, z + half_size)

        ### Let's Make Some Recursive Calls! ###
        next_size = size * self.scale_factor

        self.add_line(sub_side,pos_side, layer, add_nodes)
        self._configurable_generate_level(sub_side, next_size, blueprint[1:], layer+1)
        self._configurable_generate_level(pos_side, next_size, blueprint[1:], layer+1)

    def _generate_level_recursive(self, center: Tuple[float, float, float], 
                                 size: float, max_levels: int, 
                                 orientation: str, current_level: int) -> None:
        """
        Internal recursive method to generate H-tree levels correctly.
        """
        if current_level > max_levels:
            return

        x, y, z = center
        half_size = size * 0.5
        second_half_size = half_size * self.scale_factor

        # Draw the main line for this orientation
        if orientation == 'xy':
            self.add_line((x, y - half_size, z), (x, y + half_size, z), current_level, max_levels)
        elif orientation == 'xz':
            self.add_line((x - half_size, y, z), (x + half_size, y, z), current_level, max_levels)
        elif orientation == 'yz':
            self.add_line((x, y, z - half_size), (x, y, z + half_size), current_level, max_levels)

        # If we've reached the last level, stop
        if current_level == max_levels:
            return

        # Draw the two perpendicular lines at the ends, and recurse
        if orientation == 'xy':
            # Horizontal lines at top and bottom
            self.add_line((x - second_half_size, y + half_size, z), (x + second_half_size, y + half_size, z), current_level + 1, max_levels)
            self.add_line((x - second_half_size, y - half_size, z), (x + second_half_size, y - half_size, z), current_level + 1, max_levels)
            endpoints = [
                (x - second_half_size, y + half_size, z),
                (x + second_half_size, y + half_size, z),
                (x - second_half_size, y - half_size, z),
                (x + second_half_size, y - half_size, z)
            ]
            next_orient = 'yz'
        elif orientation == 'xz':
            # Vertical lines at left and right
            self.add_line((x - half_size, y, z + second_half_size), (x - half_size, y, z - second_half_size), current_level + 1, max_levels)
            self.add_line((x + half_size, y, z + second_half_size), (x + half_size, y, z - second_half_size), current_level + 1, max_levels)
            endpoints = [
                (x - half_size, y, z + second_half_size),
                (x + half_size, y, z + second_half_size),
                (x - half_size, y, z - second_half_size),
                (x + half_size, y, z - second_half_size)
            ]
            next_orient = 'xy'
        elif orientation == 'yz':
            # Horizontal lines at front and back
            self.add_line((x, y - second_half_size, z + half_size), (x, y + second_half_size, z + half_size), current_level + 1, max_levels)
            self.add_line((x, y - second_half_size, z - half_size), (x, y + second_half_size, z - half_size), current_level + 1, max_levels)
            endpoints = [
                (x, y - second_half_size, z + half_size),
                (x, y + second_half_size, z + half_size),
                (x, y - second_half_size, z - half_size),
                (x, y + second_half_size, z - half_size)
            ]
            next_orient = 'xz'
        else:
            return

        # Recurse for each endpoint
        if current_level + 1 < max_levels:
            next_size = size * self.scale_factor * self.scale_factor
            for endpoint in endpoints:
                self._generate_level_recursive(endpoint, next_size, max_levels, next_orient, current_level + 2)
    
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
        
        # Group lines by layer for color coding
        lines_by_layer = {}
        for line in self.lines:
            x1, y1, z1, x2, y2, z2, layer = line
            if layer not in lines_by_layer:
                lines_by_layer[layer] = []
            lines_by_layer[layer].append((x1, y1, z1, x2, y2, z2))
        
        # Add traces for each layer with different colors
        for layer in sorted(lines_by_layer.keys()):
            x_lines, y_lines, z_lines = [], [], []
            
            for line in lines_by_layer[layer]:
                x1, y1, z1, x2, y2, z2 = line
                x_lines.extend([x1, x2, None])  # None creates breaks between lines
                y_lines.extend([y1, y2, None])
                z_lines.extend([z1, z2, None])
            
            # Get color for this layer (cycle through colors)
            color = self.colors[(layer - 1) % len(self.colors)]
            
            # Calculate line width: each level is progressively thinner
            base_width = 8  # Starting thickness for level 1
            width = base_width * (0.85 ** (layer - 1))  # Each level is 70% of previous
            width = max(width, 1)  # Minimum width of 1
            
            fig.add_trace(go.Scatter3d(
                x=x_lines,
                y=y_lines,
                z=z_lines,
                mode='lines',
                line=dict(
                    color=color,
                    width=width
                ),
                name=f'Level {layer}',
                hoverinfo='skip'
            ))
        
        # Add junction points for better visualization
        all_points = list(set(self.points))  # Remove duplicates
        if all_points:
            # Collect all junction points and their sizes/colors for a single trace
            all_x_points = []
            all_y_points = []
            all_z_points = []
            all_sizes = []
            all_colors = []
            
            # Group points by layer and calculate sizes
            points_by_layer = {}
            for point_data in all_points:
                point, layer = point_data
                if layer not in points_by_layer:
                    points_by_layer[layer] = []
                points_by_layer[layer].append(point)
            
            base_size = 16  # Starting size for level 1 junctions
            
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
                junction_size = base_size * (0.8 ** (layer - 1))  # Same scaling as line width
                junction_size = max(junction_size, 1)  # Minimum size of 1
                
                # Get color for this layer (same as lines)
                if layer == 0:
                    color = 'red'
                else:
                    color = self.colors[(layer - 1) % len(self.colors)]
                
                # Add to combined arrays
                for point in points:
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
                    range=[-2.5, 2.5],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title=dict(text='Y', font=dict(color='white')), 
                    range=[-2.5, 2.5],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                zaxis=dict(
                    title=dict(text='Z', font=dict(color='white')), 
                    range=[-2.5, 2.5],
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
    
    def clear(self) -> None:
        """Clear all stored lines and points."""
        self.lines.clear()
        self.points.clear()

def visualize_custom_htree(size: float = 2.0, scale_factor: float = 0.7937, isometric: bool = False, blueprint: str = "") -> go.Figure:
    htree = HTree3D(scale_factor=scale_factor)
    htree.gen_configurable_htree((0,0,0), size, blueprint)  # Don't assign the return value

    projection_type = "Isometric" if isometric else "Perspective"
    title = f"3D H-Tree with {len(blueprint)} levels ({projection_type}, scale: {scale_factor:.4f})"
    return htree.create_plotly_figure(title, isometric)

def create_htree_visualization(levels: int = 4, size: float = 2.0, 
                             scale_factor: float = 0.7937, isometric: bool = False) -> go.Figure:
    """
    Convenience function to create and visualize an H-tree.
    
    Args:
        levels: Number of levels (1-6 recommended)
        size: Size of the initial H
        scale_factor: Scale factor for recursive branches (0.7937 default, 0.7071 alternative)
        isometric: Whether to use isometric (orthographic) projection
    
    Returns:
        Plotly Figure object
    """
    htree = HTree3D(scale_factor=scale_factor)
    htree.generate_htree((0, 0, 0), size, levels)
    
    projection_type = "Isometric" if isometric else "Perspective"
    title = f"3D H-Tree with {levels} levels ({projection_type}, scale: {scale_factor:.4f})"
    return htree.create_plotly_figure(title, isometric)

def show_with_dark_background(fig: go.Figure):
    """
    Show the figure with a full-page dark background by creating a properly styled HTML file.
    """
    # Create a dark-themed HTML file for full-page viewing
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
    
    # Insert CSS into the HTML head section
    html_content = html_content.replace('<head>', '<head>' + dark_css)
    
    # Save to a temporary file and open it
    with tempfile.NamedTemporaryFile(mode='w', suffix='_dark_htree.html', delete=False) as f:
        f.write(html_content)
        temp_path = f.name
    
    # Open the dark-themed version in browser
    webbrowser.open(f'file://{temp_path}')

def main():
    """
    Main function to demonstrate the H-tree visualizer.
    """
    print("3D H-Tree Visualizer")
    print("===================")
    
    # Get user input for number of levels

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
                        standardized_blueprint += "0"
                    elif ch in set("1yY"):
                        standardized_blueprint += "1"
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
        
    # Get user input for scale factor
    print("\nChoose scale factor:")
    print("1. 0.7937 (default - cube root of 1/2)")
    print("2. 0.7071 (sqrt(2)/2)")
    print("3. Custom value")
    
    while True:
        try:
            scale_choice = input("Enter choice (1-3, default=1): ").strip()
            if scale_choice == "" or scale_choice == "1":
                scale_factor = 0.7937
                break
            elif scale_choice == "2" or scale_choice == "0":  # Allow "0" as shortcut for 0.7071
                scale_factor = 0.7071
                break
            elif scale_choice == "3":
                custom_scale = input("Enter custom scale factor (0.1-0.9): ").strip()
                scale_factor = float(custom_scale)
                if 0.1 <= scale_factor <= 0.9:
                    break
                else:
                    print("Please enter a value between 0.1 and 0.9.")
            else:
                print("Please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number.")

    # Get user input for projection type
    print("\nChoose projection type:")
    print("1. Perspective (default - natural 3D view with depth)")
    print("2. Isometric (orthographic - technical drawing style)")
    
    while True:
        try:
            projection_choice = input("Enter choice (1-2, default=1): ").strip()
            if projection_choice == "" or projection_choice == "1":
                isometric = False
                break
            elif projection_choice == "2":
                isometric = True
                break
            else:
                print("Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

    projection_type = "Isometric" if isometric else "Perspective"
    print(f"\nGenerating 3D H-tree with {levels} levels, {projection_type.lower()} projection, and scale factor {scale_factor:.4f}...")
    
    # Create and display the visualization
    if generate_style == "1":
        fig = visualize_custom_htree(size=2.0, scale_factor=scale_factor, isometric=isometric, blueprint=final_blueprint)
    else:
        fig = create_htree_visualization(levels=levels, size=2.0, scale_factor=scale_factor, isometric=isometric)

    print("Opening interactive 3D visualization...")
    print("You can:")
    print("- Rotate: Click and drag")
    print("- Zoom: Mouse wheel or zoom controls")
    print("- Pan: Shift + click and drag")
    print("- Reset view: Double-click")
    
    # Show the interactive plot with full-page dark background
    show_with_dark_background(fig)
    
    # Optional: Save as HTML file
    save_html = input("\nSave as HTML file? (y/n, default=n): ").strip().lower()
    if save_html in ['y', 'yes']:
        projection_suffix = "_isometric" if isometric else "_perspective"
        filename = f"htree_3d_{levels}_levels{projection_suffix}.html"
        fig.write_html(filename)
        print(f"Saved as {filename}")

if __name__ == "__main__":
    main()