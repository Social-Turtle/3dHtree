import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.interpolate import griddata
from scipy.interpolate import griddata
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, BoundaryNorm, ListedColormap

A_sym, L_sym = sp.symbols('A L', real=True, positive=True)

z_expr = sp.sqrt(A_sym * L_sym) / (sp.sqrt(A_sym) + (L_sym**(sp.Rational(3,2)) / 2))
import matplotlib.pyplot as plt

TILES = 1000000
LAYER_MAX = 800

class Plot3DFramework:
    """Framework for creating 3D plots and 2D heatmaps from XYZ data."""
    
    def __init__(self, x_data=None, y_data=None, z_data=None):
        """
        Initialize the plotting framework.
        
        Args:
            x_data: X-axis data
            y_data: Y-axis data
            z_data: Z-axis data (or heat intensity for heatmap)
        """
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data
    
    def set_data(self, x_data, y_data, z_data):
        """Update the data for plotting."""
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data
    
    def plot_3d_scatter(self, title="3D Scatter Plot", xlabel="X", ylabel="Y", zlabel="Z", 
                       color='b', marker='o', figsize=(10, 8)):
        """
        Create a rotatable 3D scatter plot.
        
        Args:
            title: Plot title
            xlabel, ylabel, zlabel: Axis labels
            color: Point color
            marker: Marker style
            figsize: Figure size tuple
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        ax.scatter(self.x_data, self.y_data, self.z_data, c=color, marker=marker)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        ax.set_title(title)
        
        plt.show()
        return fig, ax
    
    def plot_3d_surface(self, title="3D Surface Plot", xlabel="X", ylabel="Y", 
                       zlabel="Z", cmap='viridis', figsize=(10, 8)):
        """
        Create a rotatable 3D surface plot.
        Requires gridded data or will grid the data automatically.
        
        Args:
            title: Plot title
            xlabel, ylabel, zlabel: Axis labels
            cmap: Colormap for surface
            figsize: Figure size tuple
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # If data is not gridded, create a grid
        if self.x_data.ndim == 1:
            xi = np.linspace(self.x_data.min(), self.x_data.max(), 50)
            yi = np.linspace(self.y_data.min(), self.y_data.max(), 50)
            X, Y = np.meshgrid(xi, yi)
            Z = griddata((self.x_data, self.y_data), self.z_data, (X, Y), method='cubic')
        else:
            X, Y, Z = self.x_data, self.y_data, self.z_data
        
        surf = ax.plot_surface(X, Y, Z, cmap=cmap)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_zlabel(zlabel)
        ax.set_title(title)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        
        plt.show()
        return fig, ax
    
    def plot_2d_heatmap(self, title="2D Heatmap", xlabel="Area", ylabel="Number of Layers", 
                       cmap='viridis', figsize=(10, 8), interpolation='nearest', plot_lines=True, norm=None):
        """
        Create a 2D heatmap where Z values represent heat intensity.
        
        Args:
            title: Plot title
            xlabel, ylabel: Axis labels
            cmap: Colormap for heatmap
            figsize: Figure size tuple
            interpolation: Interpolation method
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        if self.x_data.ndim == 1:
            xi = np.linspace(self.x_data.min(), self.x_data.max(), 100)
            yi = np.linspace(self.y_data.min(), self.y_data.max(), 100)
            X, Y = np.meshgrid(xi, yi)
            Z = griddata((self.x_data, self.y_data), self.z_data, (X, Y), method='cubic')
        else:
            X, Y, Z = self.x_data, self.y_data, self.z_data
        
        im = ax.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                        origin='lower', cmap=cmap, aspect='auto', interpolation=interpolation, norm=norm)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_ylim(bottom=1)

        from matplotlib.ticker import MultipleLocator
        y_ticks = ax.get_yticks()
        if 1 not in y_ticks:
            y_ticks = np.append([1], y_ticks[y_ticks > 1])
            ax.set_yticks(y_ticks)

        from matplotlib.ticker import PercentFormatter
        cbar = fig.colorbar(im, ax=ax, label='Improvement')
        cbar.ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        
        if plot_lines:
            # L = A^(1/3)
            A_line = np.linspace(X.min(), X.max(), 1000)
            L_cube_root = A_line**(1/3)
            ax.plot(A_line, L_cube_root, 'b--', linewidth=2, label='$L = A^{1/3}$')
            # Z = 1
            contour = ax.contour(X, Y, Z, levels=[1], colors='black', linewidths=2)

            from matplotlib.lines import Line2D
            custom_lines = [Line2D([0], [0], color='blue', linewidth=2),
                            Line2D([0], [0], color='black', linewidth=2)]
            ax.legend(custom_lines, ['Maximum Improvement', 'Limit of Improvement'], loc='best')
        plt.show()
        return fig, ax

z_func = sp.lambdify((A_sym, L_sym), z_expr, 'numpy')

def create_binary_red_green_cmap():
    """Create a binary red/green colormap with hard boundary."""
    colors = ['#ffcccb', '#90ee90']
    n_bins = 2  # Only 2 colors
    cmap = LinearSegmentedColormap.from_list('binary_red_green', colors, N=n_bins)
    return cmap

def create_red_gradient_green_cmap(n_green_bins=256):
    """
    Create a colormap with constant light red below midpoint,
    and gradient from light to dark green above midpoint.
    """
    red_color = np.array([1.0, 0.8, 0.8, 1.0])   
    light_green = np.array([0.56, 0.93, 0.56, 1.0])
    dark_green = np.array([0.0, 0.5, 0.0, 1.0])
    green_gradient = np.linspace(light_green, dark_green, n_green_bins)
    colors = np.vstack([np.tile(red_color, (n_green_bins, 1)), green_gradient])
    cmap = ListedColormap(colors)
    return cmap

if __name__ == "__main__":
    A_vals = np.linspace(1, TILES, 1000)
    L_vals = np.linspace(1, LAYER_MAX, 1000)
    A, L = np.meshgrid(A_vals, L_vals)
    z = z_func(A, L)
    vmin = np.min(z)
    vmax = np.max(z)

    plotter = Plot3DFramework(A, L, z)    
    
    norm = TwoSlopeNorm(vmin=vmin, vcenter=2.0, vmax=vmax)
    plotter.plot_2d_heatmap(title="Adding Layers to Reduce Wire Length", xlabel="Tile Count", ylabel="Number of Layers", cmap="plasma", interpolation="bilinear", norm=norm)
    
    binary_norm = BoundaryNorm([vmin, 1.0, vmax], ncolors=2)
    binary_cmap = create_binary_red_green_cmap()
    plotter.plot_2d_heatmap(title="Adding Layers to Reduce Wire Length", xlabel="Tile Count", ylabel="Number of Layers", cmap=binary_cmap, interpolation="nearest", norm=binary_norm)

    gradient_norm = TwoSlopeNorm(vmin=vmin, vcenter=1.0, vmax=vmax)
    gradient_cmap = create_red_gradient_green_cmap()
    plotter.plot_2d_heatmap(title="Adding Layers to Reduce Wire Length", xlabel="Tile Count", ylabel="Number of Layers", cmap=gradient_cmap, interpolation="nearest", norm=gradient_norm)