import plotly.graph_objects as go
from typing import Tuple
import tempfile
import math
import webbrowser

# TODO:
#   Create reasonable labels for each memory module, and each node (seperate kinds of labels)
#   Add functionality to compute distance from any module to any other module. (A node->node model might be helpful, but we may also be able to do some shortcuts from most recent ancestor, etc.)
#   Add capacity to create 3D Meshes. (and 2D ones)
#   Made memory modules their own class with their own storage, so that we can inlay our graph data from the DEV half.


PE_SIZE = 10; #Side length of a PE
LAYER_HEIGHT = 25;
GUTTER_WIDTH = 1;
# Set dimensions on the viewer window.
X_SIZE =  0;
Y_SIZE = 0;
Z_SIZE = 0;

class DataGraph():
    """
    An object to intake and handle Dev's data network
    """

class MemoryElement:
    """
    An object that represents our PEs. Can be generated with a name at 
    some location, taking up some space, and is capable of storing a 
    configurable amount of memory.

    All MemoryElement objects should be stored in a common list, 
    allowing for simple access and computation of totals.
    """
    def __init__(self, element_index, is_mesh, position, energy_per_cell = 1, cell_area = 10, memory_size = 128):
        self.memory_size = memory_size
        self.energy_per_cell = energy_per_cell
        self.cell_area = cell_area
        self.name = element_index
        self.search_length = (self.memory_size ** 0.5) * (cell_area ** 0.5) # the average length we expect to travel searching for a document in our memory
        self.search_energy = self.search_length * energy_per_cell  # the energy consumed in finding that document
        self.is_mesh = is_mesh
        self.position = position

    def print_memory():
        return
    
    def find_next(query):
        return
    
class Mesh3D:
    """
    A 3D Mesh Generator.
    """
    def __init__(self):
        self.lines = []
        self.memory_nodes = []

    def find_corner(self, blueprint):
        global X_SIZE
        global Y_SIZE
        global Z_SIZE
        corner_x = -(blueprint[0] * PE_SIZE/2 + (GUTTER_WIDTH/2 * blueprint[0] - 1))
        corner_y = -(blueprint[1] * PE_SIZE/2 + (GUTTER_WIDTH/2 * blueprint[1] - 1))
        corner_z = -(blueprint[2] * LAYER_HEIGHT/2)
        X_SIZE = abs(corner_x)
        Y_SIZE = abs(corner_y)
        Z_SIZE = abs(corner_z)
        return (corner_x, corner_y, corner_z)

    def gen_noc_layout(self, blueprint):
        """
        Create a Mesh network according to the blueprint (X,Y,Z tuple)
        """
        start_corner = self.find_corner(blueprint)
        for layer in range(blueprint[2]):
            for y_mem in range(blueprint[1]):
                for x_mem in range (blueprint[0]):
                    position = (start_corner[0]+(PE_SIZE+GUTTER_WIDTH)*x_mem, start_corner[1]+(PE_SIZE+GUTTER_WIDTH)*y_mem, start_corner[2]+layer*LAYER_HEIGHT)
                    name = layer*blueprint[1]*blueprint[0]+y_mem*blueprint[0]+x_mem
                    self.memory_nodes.append(MemoryElement(name, True, position)) # Create memory nodes with a distinct name. TEMP naming system.
                    if layer != blueprint[2]-1:
                        self.lines.append((position[0], position[1], position[2], position[0], position[1], position[2] + LAYER_HEIGHT))
                    if y_mem != blueprint[1]-1:
                        self.lines.append((position[0], position[1], position[2], position[0], position[1] + (PE_SIZE+GUTTER_WIDTH), position[2]))
                    if x_mem != blueprint[0]-1:
                        self.lines.append((position[0], position[1], position[2], position[0] + (PE_SIZE+GUTTER_WIDTH), position[1], position[2]))
        return

    def find_distance(self, node_b, node_a):
        """
        Computes the distances along the shortest wire path between nodes.
        Returns distance in an (x+y,z) tuple, to allow for after-the-fact vertical cost changes.
        """
        dist_h = abs(node_b.position[0] - node_a.position[0]) + abs(node_b.position[1] + node_a.position[1])
        dist_v = abs(node_b.position[2] - node_a.position[2])
        return (dist_h, dist_v)
    
    def compute_energy(self, node_a, node_b):
        """
        Takes two arbitrary memories, computes the power consumption to send a bit between them.        
        """
        dists = self.find_distance(self, node_a, node_b)
        
        ### TODO: Fill in whatever logic/model we base our energy consumption on... Do we actually care about values, or just linear/quadratic scaling?
        return
    
    def create_plotly_figure(self, title: str = "3D Mesh Visualization", 
                           isometric: bool = False) -> go.Figure:
        """
        Create a Plotly 3D figure from the generated Mesh.
        
        Returns:
            Plotly Figure object with interactive 3D visualization
        """
        if not self.lines:
            raise ValueError("No Mesh generated. Call gen_noc_layout() first.")
        
        fig = go.Figure()

        x_lines = []
        y_lines = []
        z_lines = []
        for line in self.lines:
            x1, y1, z1, x2, y2, z2 = line
            x_lines.extend([x1, x2, None])
            y_lines.extend([y1, y2, None])
            z_lines.extend([z1, z2, None])
                    
        fig.add_trace(go.Scatter3d(
            x=x_lines,
            y=y_lines,
            z=z_lines,
            mode='lines',
            line=dict(color="yellow", width = 1),
            name='Routing Lines',
            hoverinfo='skip'
        ))
        
        if self.memory_nodes:
            x_nodes = [node.position[0] for node in self.memory_nodes]
            y_nodes = [node.position[1] for node in self.memory_nodes]
            z_nodes = [node.position[2] for node in self.memory_nodes]
            
            fig.add_trace(go.Scatter3d(
                x=x_nodes,
                y=y_nodes,
                z=z_nodes,
                mode='markers',
                marker=dict(
                    size=8,
                    color='blue',
                    opacity=0.8,
                    line=dict(width=0)  # Remove white outline
                ),
                name='Memory Nodes',
                hoverinfo='x+y+z'
            ))
        
        # Set layout to standard
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='white')
            ),
            scene=dict(
                xaxis=dict(
                    title=dict(text='X', font=dict(color='white')), 
                    range=[-1.5*X_SIZE, 1.5*X_SIZE],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title=dict(text='Y', font=dict(color='white')), 
                    range=[-1.5*Y_SIZE, 1.5*Y_SIZE],
                    backgroundcolor='rgb(40, 40, 40)',
                    gridcolor='rgb(120, 120, 120)',
                    showbackground=True,
                    zerolinecolor='rgb(120, 120, 120)',
                    tickfont=dict(color='white')
                ),
                zaxis=dict(
                    title=dict(text='Z', font=dict(color='white')), 
                    range=[-1.5*Z_SIZE, 1.5*Z_SIZE],
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

class HTree3D:
    """
    A 3D H-tree generator.
    """
    
    def __init__(self):
        self.lines = []  # Store all line segments as (x1,y1,z1, x2,y2,z2, layer)
        self.colors = ['red', 'orange', 'green']  # Color cycle
        self.nodes = []
        self.memories = []

    def gen_noc_layout(self, blueprint: str) -> None:
        """
        Generate H-tree based on a blueprint string.
        """
        if len(blueprint) <= 0:
            return

        self._configurable_generate_level((0,0,0), blueprint, 0)

    def _configurable_generate_level(self,center, blueprint, layer) -> None:
        """Recursive structure for building abritrarily oriented (but legal) 3d htrees
        each layer passes a 1-shorter slice of instructions to the next set of levels.
        """
        global LAYER_HEIGHT
        if blueprint == "":
            return

        orientation = blueprint[0]
        total_turns = 0
        for ch in blueprint[0]:
            if ch == orientation:
                total_turns += 1

        x = center[0]
        y = center[1]
        z = center[2]

        if orientation == '0': ### X DIRECTION ###
            sub_side = (x, y, z)
            pos_side = (x, y, z)

        elif orientation == '1': ### Y DIRECTION ###
            sub_side = (x, y, z)
            pos_side = (x , y, z)
        
        elif orientation == '2': ### Z DIRECTION ###
            sub_side = (x, y, z)
            pos_side = (x , y, z)

        ### Let's Make Some Recursive Calls! ###

        #self.add_line(sub_side,pos_side, layer, add_nodes)
        #self._configurable_generate_level(sub_side, next_size, blueprint[1:], layer+1)
        #self._configurable_generate_level(pos_side, next_size, blueprint[1:], layer+1)
        return
    
    def add_line(self, point1: Tuple[float, float, float], 
                 point2: Tuple[float, float, float], layer: int, max_layers: int) -> None:
        """Add a line segment to the tree."""
        self.lines.append((*point1, *point2, layer))
        # Store points with their associated layer for size scaling
        if layer < max_layers:
            self.points.extend([(point1, layer), (point2, layer)])

    def find_distance(self, node_b, node_a):
        return
    
    def compute_energy(node_b, node_a):
        return

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

def create_viz(blueprint, network_type: bool, isometric: bool = False) -> go.Figure:
    if network_type == 1:
        noc = HTree3D()
    else:
        noc = Mesh3D()
    noc.gen_noc_layout(blueprint)        

    projection_type = "Isometric" if isometric else "Perspective"
    if network_type == 1:
        title = f"3D H-Tree with {len(blueprint)} levels ({projection_type})"
    else:
        title = f"3D Mesh with size {len(blueprint)}"

    return noc.create_plotly_figure(title, isometric)

def show_with_dark_background(fig: go.Figure):
    html_content = fig.to_html(include_plotlyjs='cdn')
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

def choose_network_type():
    """
    Gets network type choice from the user. Returns 0 for mesh, 1 for htree.
    """
    while True:
        network_type = input("Select your network type (1 = Htree, 0 = Mesh): ").strip()
        if int(network_type) == 0 or int(network_type) == 1:
            return int(network_type)
        else:
            print("Input invalid. Please try again.")

def create_blueprint(mode):
    if int(mode) == 1:
        print("\nDefine your Htree as a no-space string, starting from the core dimension.")
        print("0,x,X = x-dimension")
        print("1,y,Y = y-dimension")
        print("2,z,Z = z-dimension")
        while True:
            try:
                input_blueprint = input("Enter htree as a no-space string: ").strip()
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
        return standardized_blueprint
    else: # generate a mesh network
        while True:
            mesh_X = input("Enter X dimension of the mesh: ").strip()
            mesh_Y = input("Enter Y dimension of the mesh: ").strip()
            mesh_Z = input("Enter Z dimension of the mesh: ").strip()
            if mesh_X.isdigit() and mesh_Y.isdigit() and mesh_Z.isdigit() and mesh_X != "0" and mesh_Y != "0" and mesh_Z != "0" :
                break
            else:
                print("Only nonzero integer inputs accepted.")
        print("Constructing mesh with dimensions X,Y,Z of: (" + str(mesh_X) + ", " + str(mesh_Y) + ", " + str(mesh_Z) + ")")
        return (int(mesh_X),int(mesh_Y),int(mesh_Z))

def choose_projection():
    print("\nChoose projection type:")
    print("1. Isometric")
    print("2. Perspective")
    while True:
        try:
            projection_choice = input("Enter choice (1-2, default=1): ").strip()
            if projection_choice == "2":
                return False
            else:
                return True
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("3D Memory Network Simulation Environment")
    print("========================================")
    network_type = choose_network_type()
    final_blueprint = create_blueprint(network_type) #  WARNING: -- output is a string for htree and a tuple for mesh --
    isometric = choose_projection()
    projection_type = "Isometric" if isometric else "Perspective"
    print(f"\nGenerating NOC in {projection_type.lower()} projection.")
    
    fig = create_viz(final_blueprint, network_type)
    show_with_dark_background(fig)

    save_html = input("\nSave as HTML file? (y/n, default=n): ").strip().lower()
    if save_html in ['y', 'yes']:
        projection_suffix = "_isometric" if isometric else "_perspective"
        filename = f"htree_3d_{len(final_blueprint)}_levels{projection_suffix}.html"
        fig.write_html(filename)
        print(f"Saved as {filename}")

if __name__ == "__main__":
    main()