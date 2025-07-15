"""
Demo script for the 3D H-tree visualizer.
Shows different examples with various numbers of layers.
"""

from htreevis import create_htree_visualization
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_comparison_view():
    """Create a comparison view with different layer counts."""
    
    # Create subplots (2x2 grid)
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "scene"}, {"type": "scene"}],
               [{"type": "scene"}, {"type": "scene"}]],
        subplot_titles=('2 Layers', '3 Layers', '4 Layers', '5 Layers'),
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # Generate H-trees for different layer counts
    for i, layers in enumerate([2, 3, 4, 5], 1):
        htree_fig = create_htree_visualization(layers=layers, size=1.0)
        
        # Extract the traces from the individual figure
        for trace in htree_fig.data:
            # Determine subplot position
            row = 1 if i <= 2 else 2
            col = i if i <= 2 else i - 2
            
            fig.add_trace(trace, row=row, col=col)
    
    # Update layout
    fig.update_layout(
        title="3D H-Tree Comparison (Different Layer Counts)",
        height=800,
        showlegend=False
    )
    
    return fig

def demo_single_views():
    """Show individual H-trees with different layer counts."""
    
    layer_counts = [2, 3, 4, 5]
    
    print("3D H-Tree Demo")
    print("==============\n")
    
    for layers in layer_counts:
        print(f"Generating H-tree with {layers} layers...")
        fig = create_htree_visualization(layers=layers, size=2.0)
        
        # Show each visualization
        fig.show()
        
        # Ask user if they want to continue
        if layers < max(layer_counts):
            response = input(f"\nPress Enter to see {layers + 1} layers (or 'q' to quit): ")
            if response.lower() == 'q':
                break
            print()

def main():
    """Main demo function."""
    print("3D H-Tree Visualizer Demo")
    print("========================\n")
    
    print("Choose demo mode:")
    print("1. Individual views (one at a time)")
    print("2. Comparison view (all in one figure)")
    print("3. Custom single view")
    
    while True:
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                demo_single_views()
                break
            elif choice == "2":
                print("Creating comparison view...")
                fig = create_comparison_view()
                fig.show()
                break
            elif choice == "3":
                layers = int(input("Enter number of layers (1-6): "))
                if 1 <= layers <= 6:
                    fig = create_htree_visualization(layers=layers, size=2.0)
                    fig.show()
                    break
                else:
                    print("Please enter a number between 1 and 6.")
            else:
                print("Please enter 1, 2, or 3.")
                
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nDemo cancelled.")
            break

if __name__ == "__main__":
    main()
