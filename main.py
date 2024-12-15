import os
import exifread
import folium


def extract_metadata(file_path):
    with open(file_path, 'rb') as file:
        tags = exifread.process_file(file)
        return {tag: tags[tag] for tag in tags.keys()}


def get_geotags(metadata):
    def convert_to_degrees(value):
        d, m, s = [float(x.num) / float(x.den) for x in value.values]
        return d + (m / 60.0) + (s / 3600.0)

    try:
        gps_latitude = metadata["GPS GPSLatitude"]
        gps_latitude_ref = metadata["GPS GPSLatitudeRef"]
        gps_longitude = metadata["GPS GPSLongitude"]
        gps_longitude_ref = metadata["GPS GPSLongitudeRef"]

        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref.values[0] != "N":
            lat = -lat

        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref.values[0] != "E":
            lon = -lon

        return lat, lon
    except KeyError:
        return None


def visualize_geotags(geotags, output_map):
    map = folium.Map(location=geotags, zoom_start=12)
    folium.Marker(geotags, popup="Location").add_to(map)
    map.save(output_map)

def print_colored(message, color='green'):
    color_codes = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    print(f"{color_codes[color]}{message}{color_codes['end']}")


def process_files_in_directory(directory):
    if not os.path.exists("maps"):
        os.makedirs("maps")

    print_colored("Starting processing files...\n", 'blue')

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path) and file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            print_colored(f"\nProcessing: {filename}...", 'yellow')

            metadata = extract_metadata(file_path)
            print_colored(f"Extracted metadata for {filename}: ", 'green')
            print(metadata)

            geotags = get_geotags(metadata)
            if geotags:
                print_colored(f"Geotags found for {filename}: {geotags}", 'green')
                output_map = os.path.join("maps", f"{filename}_geotag_map.html")
                visualize_geotags(geotags, output_map)
                print_colored(f"Map saved to: {output_map}", 'green')
            else:
                print_colored(f"No geotags found for {filename}.", 'red')
        else:
            print_colored(f"Skipping {filename} (not a valid image file).", 'red')

# Ru
if __name__ == "__main__":
    sample_directory = "sample_files"  # Directory with EXIF images
    process_files_in_directory(sample_directory)
