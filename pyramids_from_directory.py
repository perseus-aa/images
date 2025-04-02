from pathlib import Path
import pyvips
import sys
import logging

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

def convert_to_pyramidal_tif(input_dir, target_dir):
    """
    Recursively converts all image files in the input directory to pyramidal TIFF files and saves them in the target directory.

    :param input_dir: Path to the directory containing input image files.
    :param target_dir: Path to the directory where output TIFF files will be saved.
    """
    input_path = Path(input_dir)
    target_path = Path(target_dir)

    # Ensure the target directory exists
    target_path.mkdir(parents=True, exist_ok=True)

    # Iterate over all files recursively in the input directory
    for file in input_path.rglob("*.*"):
        if not file.is_file():
            continue

        # Skip files that are not images (basic check by extension)
        if file.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}:
            logger.warning(f"Skipping non-image file: {file.name}")
            continue

        try:
            # Load the image using pyvips
            image = pyvips.Image.new_from_file(str(file), access="sequential")

            # Construct the output file path, preserving directory structure
            relative_path = file.relative_to(input_path)
            output_file = target_path / relative_path.with_suffix(".tif")
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Save the image as a pyramidal TIFF
            image.tiffsave(
                str(output_file),
                tile=True,
                pyramid=True,
                compression="jpeg",
                tile_width=256,
                tile_height=256
            )

            logger.info(f"Converted {file} to pyramidal TIFF: {output_file}")
        except Exception as e:
            logger.error(f"Failed to convert {file}: {e}")

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert image files to pyramidal TIFF format recursively.")
    parser.add_argument("input_dir", help="Directory containing input image files.")
    parser.add_argument("target_dir", help="Directory to save the output pyramidal TIFF files.")

    args = parser.parse_args()

    convert_to_pyramidal_tif(args.input_dir, args.target_dir)
