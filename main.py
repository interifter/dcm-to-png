from pathlib import Path
import click
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_voi_lut
import png
import numpy as np


@click.group
def main():
    """Convert .dcm to .png files"""
    ...


@main.command
@click.option("--input", "-i", required=True)
@click.option("--output", "-o", required=True)
@click.option("--ignore", "--skip-extension-check", is_flag=True, help="Ignore the file extension checks")
def convert(input: str, output: str, ignore: bool):
    if not input.endswith(".dcm") and not ignore:
        raise click.ClickException(f"Input must have a .dcm file extension")
    if not output.endswith(".png") and not ignore:
        raise click.ClickException(f"Output must end with .png")
    dcm_content = dcmread(input)
    if "WindowWidth" in dcm_content:
        ...
    # https://stackoverflow.com/q/60219622
    input = Path(input)
    output: Path = Path(output)
    windowed = apply_voi_lut(dcm_content.pixel_array, dcm_content)
    shape = dcm_content.pixel_array.shape

    # Convert to float to avoid overflow or underflow losses.
    image_2d = dcm_content.pixel_array.astype(float)

    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0

    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)

    # Write the PNG file
    with output.open("wb") as png_file:
        w = png.Writer(shape[1], shape[0], greyscale=True)
        w.write(png_file, image_2d_scaled)

if __name__ == "__main__":
    main()