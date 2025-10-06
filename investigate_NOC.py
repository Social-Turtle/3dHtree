import sys
import logging
import datetime
import os
sys.path.append('./3dHtree')  # Add the 3dHtree directory to path
sys.path.append('../HNSW-NoC/hnsw.py')  # Add the 3dHtree directory to path
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

def main():
    # load dummyInput as an input file.
    # parse standard variables - N_MEMORIES, MEMORY_CAPACITY, N_LAYERS, PE_SIDE_LENGTH, GUTTER_WIDTH, LAYER_HEIGHT, PATH_TO_DATA, CLUSTER_METHOD

    # Call noc.py to create the graphs themselves.
    pass

if __name__ == "__main__":
    logger.info("Starting NOC analysis session")
    
    # Run the interactive explorer
    main()