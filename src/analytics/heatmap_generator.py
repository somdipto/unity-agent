"""
Heatmap Generator - Specialized module for creating visual heatmaps from gameplay data
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, Tuple, List, Optional


class HeatmapGenerator:
    """
    Generates visual heatmaps showing agent activity, difficulty, and engagement
    """
    
    def __init__(self):
        self.heatmap_data = {}
    
    def create_activity_heatmap(
        self, 
        positions: List[Tuple[float, float]], 
        weights: Optional[List[float]] = None,
        grid_size: Tuple[int, int] = (50, 50),
        output_path: str = None
    ) -> np.ndarray:
        """
        Create a heatmap showing agent activity based on position data
        
        Args:
            positions: List of (x, z) coordinates where agents were active
            weights: Optional weights for each position (e.g., time spent)
            grid_size: Dimensions of the grid (width, height)
            output_path: Where to save the heatmap image
        """
        if not positions:
            return np.zeros((1, 1))
        
        # Normalize positions to fit in grid
        xs = [p[0] for p in positions]
        zs = [p[1] for p in positions]
        
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        
        # Create grid
        heatmap = np.zeros(grid_size)
        
        # Calculate cell size
        cell_width = (max_x - min_x) / grid_size[0] if grid_size[0] > 0 else 1
        cell_height = (max_z - min_z) / grid_size[1] if grid_size[1] > 0 else 1
        
        # Populate heatmap grid
        for i, (x, z) in enumerate(positions):
            # Convert world coordinates to grid coordinates
            grid_x = int((x - min_x) / cell_width) if cell_width > 0 else 0
            grid_z = int((z - min_z) / cell_height) if cell_height > 0 else 0
            
            # Clamp to grid bounds
            grid_x = max(0, min(grid_x, grid_size[0] - 1))
            grid_z = max(0, min(grid_z, grid_size[1] - 1))
            
            # Add weight if provided
            weight = weights[i] if weights else 1.0
            heatmap[grid_z, grid_x] += weight
        
        # Visualize if output path provided
        if output_path:
            self._visualize_heatmap(heatmap, min_x, max_x, min_z, max_z, output_path, "Activity")
        
        return heatmap
    
    def create_difficulty_heatmap(
        self, 
        positions: List[Tuple[float, float]], 
        difficulty_scores: List[float],
        grid_size: Tuple[int, int] = (50, 50),
        output_path: str = None
    ) -> np.ndarray:
        """
        Create a heatmap showing difficulty levels in different areas
        
        Args:
            positions: List of (x, z) coordinates where difficulty was assessed
            difficulty_scores: Difficulty score for each position
            grid_size: Dimensions of the grid (width, height)
            output_path: Where to save the heatmap image
        """
        if not positions or len(positions) != len(difficulty_scores):
            return np.zeros((1, 1))
        
        # Normalize positions to fit in grid
        xs = [p[0] for p in positions]
        zs = [p[1] for p in positions]
        
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        
        # Create grid
        heatmap = np.zeros(grid_size)
        
        # Calculate cell size
        cell_width = (max_x - min_x) / grid_size[0] if grid_size[0] > 0 else 1
        cell_height = (max_z - min_z) / grid_size[1] if grid_size[1] > 0 else 1
        
        # Populate heatmap grid with difficulty scores
        for i, (x, z) in enumerate(positions):
            # Convert world coordinates to grid coordinates
            grid_x = int((x - min_x) / cell_width) if cell_width > 0 else 0
            grid_z = int((z - min_z) / cell_height) if cell_height > 0 else 0
            
            # Clamp to grid bounds
            grid_x = max(0, min(grid_x, grid_size[0] - 1))
            grid_z = max(0, min(grid_z, grid_size[1] - 1))
            
            # Add difficulty score for this cell
            heatmap[grid_z, grid_x] += difficulty_scores[i]
        
        # Apply normalization to average scores per cell
        # Count occurrences to compute average
        occurrence_grid = np.zeros(grid_size)
        for i, (x, z) in enumerate(positions):
            grid_x = int((x - min_x) / cell_width) if cell_width > 0 else 0
            grid_z = int((z - min_z) / cell_height) if cell_height > 0 else 0
            
            grid_x = max(0, min(grid_x, grid_size[0] - 1))
            grid_z = max(0, min(grid_z, grid_size[1] - 1))
            
            occurrence_grid[grid_z, grid_x] += 1
        
        # Calculate average difficulty per cell
        with np.errstate(divide='ignore', invalid='ignore'):
            heatmap = np.divide(heatmap, occurrence_grid, out=np.zeros_like(heatmap), where=occurrence_grid!=0)
        
        # Visualize if output path provided
        if output_path:
            self._visualize_heatmap(heatmap, min_x, max_x, min_z, max_z, output_path, "Difficulty")
        
        return heatmap
    
    def create_engagement_heatmap(
        self, 
        positions: List[Tuple[float, float]], 
        engagement_levels: List[float],
        grid_size: Tuple[int, int] = (50, 50),
        output_path: str = None
    ) -> np.ndarray:
        """
        Create a heatmap showing engagement levels in different areas
        
        Args:
            positions: List of (x, z) coordinates where engagement was assessed
            engagement_levels: Engagement level (0.0 to 1.0) for each position
            grid_size: Dimensions of the grid (width, height)
            output_path: Where to save the heatmap image
        """
        if not positions or len(positions) != len(engagement_levels):
            return np.zeros((1, 1))
        
        # Normalize positions to fit in grid
        xs = [p[0] for p in positions]
        zs = [p[1] for p in positions]
        
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        
        # Create grid
        heatmap = np.zeros(grid_size)
        
        # Calculate cell size
        cell_width = (max_x - min_x) / grid_size[0] if grid_size[0] > 0 else 1
        cell_height = (max_z - min_z) / grid_size[1] if grid_size[1] > 0 else 1
        
        # Populate heatmap grid with engagement levels
        for i, (x, z) in enumerate(positions):
            # Convert world coordinates to grid coordinates
            grid_x = int((x - min_x) / cell_width) if cell_width > 0 else 0
            grid_z = int((z - min_z) / cell_height) if cell_height > 0 else 0
            
            # Clamp to grid bounds
            grid_x = max(0, min(grid_x, grid_size[0] - 1))
            grid_z = max(0, min(grid_z, grid_size[1] - 1))
            
            # Add engagement level to this cell
            heatmap[grid_z, grid_x] += engagement_levels[i]
        
        # Apply normalization to average scores per cell
        occurrence_grid = np.zeros(grid_size)
        for i, (x, z) in enumerate(positions):
            grid_x = int((x - min_x) / cell_width) if cell_width > 0 else 0
            grid_z = int((z - min_z) / cell_height) if cell_height > 0 else 0
            
            grid_x = max(0, min(grid_x, grid_size[0] - 1))
            grid_z = max(0, min(grid_z, grid_size[1] - 1))
            
            occurrence_grid[grid_z, grid_x] += 1
        
        # Calculate average engagement per cell
        with np.errstate(divide='ignore', invalid='ignore'):
            heatmap = np.divide(heatmap, occurrence_grid, out=np.zeros_like(heatmap), where=occurrence_grid!=0)
        
        # Visualize if output path provided
        if output_path:
            self._visualize_heatmap(heatmap, min_x, max_x, min_z, max_z, output_path, "Engagement")
        
        return heatmap
    
    def _visualize_heatmap(
        self, 
        heatmap: np.ndarray, 
        min_x: float, 
        max_x: float, 
        min_z: float, 
        max_z: float, 
        output_path: str, 
        title: str
    ):
        """Private method to visualize and save a heatmap"""
        plt.figure(figsize=(12, 8))
        
        # Create custom colormap
        if title == "Difficulty":
            colors = ['skyblue', 'yellow', 'orange', 'red', 'darkred']
        elif title == "Engagement":
            colors = ['lightgray', 'lightgreen', 'yellow', 'orange', 'darkred']
        else:  # Activity
            colors = ['white', 'lightblue', 'blue', 'purple', 'darkred']
        
        n_bins = 256
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # Plot heatmap
        im = plt.imshow(
            heatmap, 
            extent=[min_x, max_x, min_z, max_z], 
            origin='lower', 
            cmap=cmap, 
            aspect='auto',
            vmin=0,  # Explicitly set min value
            vmax=heatmap.max() if heatmap.max() > 0 else 1  # Handle case where all values are 0
        )
        
        plt.colorbar(im, label=f'{title} Level')
        plt.title(f'{title} Heatmap')
        plt.xlabel('X Coordinate')
        plt.ylabel('Z Coordinate')
        
        # Save the plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def combine_heatmaps(
        self, 
        activity_map: np.ndarray, 
        difficulty_map: np.ndarray, 
        engagement_map: np.ndarray,
        output_path: str = None
    ) -> np.ndarray:
        """
        Combine multiple heatmaps into a single visualization showing all metrics
        """
        # Determine the size of the combined map
        max_height = max(activity_map.shape[0], difficulty_map.shape[0], engagement_map.shape[0])
        max_width = max(activity_map.shape[1], difficulty_map.shape[1], engagement_map.shape[1])
        
        # Create a combined map using weighted average
        combined = np.zeros((max_height, max_width, 3))  # RGB channels
        
        # Normalize each heatmap to 0-1 range
        def normalize(heatmap):
            if heatmap.max() == 0:
                return heatmap
            return (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())
        
        # Pad heatmaps to same size if needed
        def pad_to_size(heatmap, target_shape):
            padded = np.zeros(target_shape)
            padded[:heatmap.shape[0], :heatmap.shape[1]] = heatmap
            return padded
        
        target_shape = (max_height, max_width)
        norm_activity = normalize(pad_to_size(activity_map, target_shape))
        norm_difficulty = normalize(pad_to_size(difficulty_map, target_shape))
        norm_engagement = normalize(pad_to_size(engagement_map, target_shape))
        
        # Assign to RGB channels
        combined[:, :, 0] = norm_activity    # Red channel - Activity
        combined[:, :, 1] = norm_engagement # Green channel - Engagement
        combined[:, :, 2] = norm_difficulty # Blue channel - Difficulty
        
        if output_path:
            plt.figure(figsize=(12, 8))
            plt.imshow(combined, extent=[0, max_width, 0, max_height], origin='lower', aspect='auto')
            plt.title('Combined Metrics: RGB = Activity/Engagement/Difficulty')
            plt.xlabel('Grid X')
            plt.ylabel('Grid Z')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return combined