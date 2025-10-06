import sys
import logging
import datetime
import os
sys.path.append('./3dHtree')  # Add the 3dHtree directory to path
from htreevis import Mesh3D, HTree3D, MemoryElement

# Set up logging
def setup_logging():
    """Set up logging to file with timestamps."""
    log_filename = os.path.join(os.path.dirname(__file__), f"noc_analysis_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, mode='a'),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class NOC:
    """
    A Network-on-Chip class that wraps either a Mesh3D or HTree3D instance
    and provides a unified interface for working with NOCs.
    """
    
    def __init__(self, network_type='mesh'):
        """
        Initialize NOC with specified network type.
        
        Args:
            network_type (str): 'mesh' or 'htree'
        """
        self.network_type = network_type.lower()
        
        if self.network_type == 'mesh':
            self.noc = Mesh3D()
        elif self.network_type == 'htree':
            self.noc = HTree3D()
        else:
            raise ValueError("network_type must be 'mesh' or 'htree'")
        
        logger.info(f"Created NOC instance of type: {self.network_type}")
    
    def generate_layout(self, blueprint):
        """
        Generate the NOC layout based on blueprint.
        
        Args:
            blueprint: For mesh - tuple (x, y, z), for htree - string like "012"
        """
        self.noc.gen_noc_layout(blueprint)
        message = f"Generated {self.network_type} layout with blueprint: {blueprint}"
        print(message)
        logger.info(message)
    
    def visualize(self, title=None, isometric=True):
        """
        Create and return a Plotly figure of the NOC.
        
        Args:
            title (str): Custom title for the visualization
            isometric (bool): Use isometric projection if True
        
        Returns:
            plotly.graph_objects.Figure
        """
        if title is None:
            title = f"3D {self.network_type.title()} NOC Visualization"
        
        fig = self.noc.create_plotly_figure(title, isometric)
        logger.info(f"Generated visualization: {title}, isometric: {isometric}")
        return fig
    
    def get_memory_nodes(self):
        """Return list of memory nodes (for Mesh3D only)."""
        if hasattr(self.noc, 'memory_nodes'):
            return self.noc.memory_nodes
        else:
            print("Memory nodes not available for this NOC type")
            return []
    
    def get_lines(self):
        """Return list of connection lines."""
        return self.noc.lines
    
    def print_stats(self):
        """Print basic statistics about the NOC."""
        stats_msg = f"\n=== {self.network_type.upper()} NOC Statistics ==="
        print(stats_msg)
        logger.info(stats_msg.strip())
        
        lines_msg = f"Total lines: {len(self.noc.lines)}"
        print(lines_msg)
        logger.info(lines_msg)
        
        if hasattr(self.noc, 'memory_nodes'):
            nodes_msg = f"Total memory nodes: {len(self.noc.memory_nodes)}"
            print(nodes_msg)
            logger.info(nodes_msg)
            
            if self.noc.memory_nodes:
                first_pos = f"First node position: {self.noc.memory_nodes[0].position}"
                last_pos = f"Last node position: {self.noc.memory_nodes[-1].position}"
                print(first_pos)
                print(last_pos)
                logger.info(first_pos)
                logger.info(last_pos)
        
        if hasattr(self.noc, 'points'):
            points_msg = f"Total junction points: {len(self.noc.points)}"
            print(points_msg)
            logger.info(points_msg)
    
    def compute_distance(self, node_a_idx, node_b_idx):
        """
        Compute distance between two memory nodes (Mesh3D only).
        
        Args:
            node_a_idx (int): Index of first node
            node_b_idx (int): Index of second node
        
        Returns:
            tuple: (horizontal_distance, vertical_distance) or None
        """
        if not hasattr(self.noc, 'memory_nodes') or not hasattr(self.noc, 'find_distance'):
            error_msg = "Distance computation not available for this NOC type"
            print(error_msg)
            logger.warning(error_msg)
            return None
        
        if (node_a_idx >= len(self.noc.memory_nodes) or 
            node_b_idx >= len(self.noc.memory_nodes) or
            node_a_idx < 0 or node_b_idx < 0):
            error_msg = f"Node indices out of range. Available nodes: 0-{len(self.noc.memory_nodes)-1}"
            print(error_msg)
            logger.warning(error_msg)
            return None
        
        node_a = self.noc.memory_nodes[node_a_idx]
        node_b = self.noc.memory_nodes[node_b_idx]
        
        distance = self.noc.find_distance(node_b, node_a)
        
        distance_msg = f"Distance between nodes {node_a_idx} and {node_b_idx}: {distance}"
        print(distance_msg)
        logger.info(distance_msg)
        
        return distance

def interactive_distance_calculator(noc):
    """Interactive distance calculation for the current NOC."""
    if not hasattr(noc.noc, 'memory_nodes') or not noc.noc.memory_nodes:
        print("No memory nodes available for distance calculation.")
        logger.warning("Distance calculation attempted on NOC without memory nodes")
        return
    
    max_node = len(noc.noc.memory_nodes) - 1
    print(f"\n=== Distance Calculator ===")
    print(f"Available nodes: 0 to {max_node}")
    
    while True:
        try:
            print("\nEnter node indices (or 'q' to quit):")
            node_a_input = input("First node index: ").strip()
            if node_a_input.lower() == 'q':
                break
                
            node_b_input = input("Second node index: ").strip()
            if node_b_input.lower() == 'q':
                break
            
            node_a = int(node_a_input)
            node_b = int(node_b_input)
            
            noc.compute_distance(node_a, node_b)
            
        except ValueError:
            print("Please enter valid integer indices or 'q' to quit.")
        except KeyboardInterrupt:
            print("\nExiting distance calculator...")
            break

def interactive_noc_explorer():
    """Interactive function to build and explore NOCs continuously."""
    logger.info("Started interactive NOC explorer")
    
    noc = None
    
    while True:
        print("\n" + "="*50)
        print("=== Interactive NOC Explorer ===")
        print("1. Create new NOC")
        print("2. Show current NOC stats")
        print("3. Visualize current NOC")
        print("4. Calculate distances between nodes")
        print("5. Quit")
        print("="*50)
        
        try:
            choice = input("Choose an option (1-5): ").strip()
            
            if choice == '1':
                # Create new NOC
                while True:
                    noc_type = input("Choose NOC type (mesh/htree): ").strip().lower()
                    if noc_type in ['mesh', 'htree']:
                        break
                    print("Please enter 'mesh' or 'htree'")
                
                noc = NOC(noc_type)
                
                # Get blueprint
                if noc_type == 'mesh':
                    print("Enter mesh dimensions:")
                    try:
                        x = int(input("X dimension: "))
                        y = int(input("Y dimension: "))
                        z = int(input("Z dimension: "))
                        blueprint = (x, y, z)
                    except ValueError:
                        print("Invalid dimensions. Using default 3x3x2.")
                        blueprint = (3, 3, 2)
                else:
                    blueprint = input("Enter H-tree pattern (e.g., '012'): ").strip()
                    if not blueprint:
                        blueprint = "012"
                        print("Using default pattern: 012")
                
                noc.generate_layout(blueprint)
                noc.print_stats()
            
            elif choice == '2':
                if noc is None:
                    print("No NOC created yet. Choose option 1 first.")
                else:
                    noc.print_stats()
            
            elif choice == '3':
                if noc is None:
                    print("No NOC created yet. Choose option 1 first.")
                else:
                    isometric = input("Use isometric projection? (y/n, default=y): ").strip().lower()
                    isometric = isometric != 'n'  # Default to True unless explicitly 'n'
                    
                    fig = noc.visualize(isometric=isometric)
                    fig.show()
                    print("Visualization displayed. Close the browser tab when done viewing.")
            
            elif choice == '4':
                if noc is None:
                    print("No NOC created yet. Choose option 1 first.")
                else:
                    interactive_distance_calculator(noc)
            
            elif choice == '5':
                print("Goodbye!")
                logger.info("Interactive NOC explorer session ended")
                break
            
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            logger.info("Interactive NOC explorer session interrupted")
            break
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            logger.error(error_msg)

# Example usage functions
def create_sample_mesh():
    """Create a sample 3x3x2 mesh NOC."""
    noc = NOC('mesh')
    noc.generate_layout((3, 3, 2))
    return noc

def create_sample_htree():
    """Create a sample H-tree NOC."""
    noc = NOC('htree')
    noc.generate_layout("012")  # 3-level htree
    return noc

if __name__ == "__main__":
    logger.info("Starting NOC analysis session")
    
    # Run the interactive explorer
    interactive_noc_explorer()