# update_pyramids.py

from pathlib import Path
import pyvips
import sys
import logging
import json

# Configure logging
logger = logging.getLogger("updater_pyramids")
logger.setLevel(logging.INFO)

# Create separate handlers for stdout and stderr
info_handler = logging.StreamHandler(sys.stdout)
info_handler.setLevel(logging.INFO)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setLevel(logging.ERROR)

# Define log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)

# Ensure third-party loggers (like pyvips) don't propagate messages to this logger
logger.propagate = False

# Suppress excessive logging from pyvips
logging.getLogger("pyvips").setLevel(logging.WARNING)

def update_pyramids(index_file, target_dir):
    """ Iterates over the entries in the images/indexes/extant/*.json file and
    generates a pyramidal tiff if one doesn't already exist in the target_dir.
    
    """

    logger.info(f"updating pyramids for {index_file}")

    index_path:Path = Path(index_file)
    target_path:Path = Path(target_dir)

    with open(index_path, 'r') as f:
        index = json.load(f)

    logger.info(f"{index_path} has {len(index)} entries")
    # iterate over the entries in the index. Skip processing
    # if a tif already exists in the target directory.
    for k, entry in index.items():
        
        # prioritize archival images
        selected_img_file = entry.get('archival') or entry.get('images') or entry.get('restricted')
        img_file = Path(selected_img_file)
        logger.info(f"choosing {img_file}")
        output_file_path:Path = target_path / img_file.with_suffix('.tif').name

        if output_file_path.exists():
            logger.info(f"skipping {img_file}; {output_file_path} already exists")
        else:
            logger.info(f"processing {img_file}")
            try:
                image = pyvips.Image.new_from_file(img_file, access="sequential")
                
                # Save the image as a pyramidal TIFF
                image.tiffsave(
                    str(output_file_path),
                    tile=True,
                    pyramid=True,
                    compression="jpeg",
                    tile_width=256,
                    tile_height=256)
                
                logger.info(f"Converted {img_file} to pyramidal TIFF: {output_file_path}")

            except Exception as e:
                logger.error(f"Failed to convert {img_file}: {e}")

    logger.info(f"finished updating files in {index_file}")



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update pyramidal TIFF files.")
    parser.add_argument("image_index", help="Directory of mappings of objects to extant image files")
    parser.add_argument("target_dir", help="Directory to save the output pyramidal TIFF files.")

    args = parser.parse_args()

    update_pyramids(args.image_index, args.target_dir)
