from pathlib import Path
import pyvips
import sys
import logging
import json

# Configure logging
logger = logging.getLogger("convert_to_pyramidal_tif")
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

def convert_to_pyramidal_tif(image_map_file, target_dir):
    """
    Converts image files in the image map to pyramidal TIFF files and saves them in the target directory.

    :param image_map: Path to the directory containing input image files.
    :param target_dir: Path to the directory where output TIFF files will be saved.
    """
    target_path = Path(target_dir)

    with open(image_map_file, 'r') as f:
        image_map = json.load(f)

    # Ensure the target directory exists
    target_path.mkdir(parents=True, exist_ok=True)

    # iterate over entries in the image_map
    for k, entry in image_map.items():
        # prioritize archival images
        selected_img_file = entry.get('archival') or entry.get('images') or entry.get('restricted')
        img_file = Path(selected_img_file)
        output_file_path = target_path / img_file.with_suffix('.tif').name

        try:
            image = pyvips.Image.new_from_file(img_file, access="sequential")

            # Save the image as a pyramidal TIFF
            image.tiffsave(
                str(output_file_path),
                tile=True,
                pyramid=True,
                compression="jpeg",
                tile_width=256,
                tile_height=256
                )
            
            logger.info(f"Converted {img_file} to pyramidal TIFF: {output_file_path}")

        except Exception as e:
            logger.error(f"Failed to convert {img_file}: {e}")
    

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert image files to pyramidal TIFF format recursively.")
    parser.add_argument("image_map", help="File containing map of image names to image files.")
    parser.add_argument("target_dir", help="Directory to save the output pyramidal TIFF files.")

    args = parser.parse_args()

    convert_to_pyramidal_tif(args.image_map, args.target_dir)
