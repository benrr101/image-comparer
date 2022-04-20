import dominate
import imagehash
import os
import sys

from PIL import Image, ImageFile
from datetime import datetime
from dominate.tags import *
from dominate.util import raw

ImageFile.LOAD_TRUNCATED_IMAGES = True
HASHING_ALGORITHM = imagehash.average_hash
HASH_SIZE = 48
THRESHOLD = 25


class HashedImage:
    # CONSTRUCTOR ##########################################################

    def __init__(self, path):
        """
        Initializes a new instance of the image
        :param path:
        """
        self._path = path

        image = Image.open(path)
        self._height = image.size[1]
        self._width = image.size[0]
        self._last_modified = os.path.getmtime(path)
        self._hash = HASHING_ALGORITHM(image, hash_size=HASH_SIZE)

    # PROPERTIES ###########################################################

    @property
    def hash(self):
        return self._hash

    @property
    def height(self):
        return self._height

    @property
    def last_modified(self):
        return self._last_modified

    @property
    def path(self):
        return self._path

    @property
    def width(self):
        return self._width


def main():
    if len(sys.argv) < 2:
        print_usage()
        exit(1)

    # Step 1: Validate the paths
    folder_path_list = sys.argv[1:]
    print('Looking for images in these folders:')
    for folder_path in folder_path_list:
        if not os.path.exists(folder_path):
            print('-------')
            print(f'Folder {folder_path} does not exist!')
            print('exiting.')
            exit(1)

        print(f'  {folder_path}')

    # Step 2: Discover images and calculate hashes
    print()
    print('Discovering images', end='')

    images = {}
    invalid_paths = []
    images_discovered = 0
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                image_path = os.path.join(root, file)
                try:
                    image = HashedImage(image_path)
                    images[image] = []
                except:
                    invalid_paths.append(image_path)

                # Show progress
                images_discovered += 1
                if images_discovered % 10 == 0:
                    print('.', end='')

    # Step 3: Find similar files based on hash
    print()
    print('Finding similar files', end='')

    images_processed = 0
    for image_a in images.keys():
        for image_b in images.keys():
            # Don't compare the image to itself
            if image_a == image_b:
                continue

            hash_difference = image_a.hash - image_b.hash
            if hash_difference <= THRESHOLD:
                images[image_a].append((image_b, hash_difference))

        # Show progress
        images_processed += 1
        if images_processed % 10 == 0:
            print('.', end='')

    # Step 4: Generate report
    print()
    print('Generating report', end='')

    reports_generated = 0
    generated_reports = set()
    doc = dominate.document(title='image-comparer report', )
    with doc.head:
        script_path = os.path.join(os.path.dirname(__file__), "report-script.js")
        script_file = open(script_path, "r")
        script_str = script_file.read()
        script_file.close()
        script(raw(script_str), type='text/javascript')

        css_path = os.path.join(os.path.dirname(__file__), "report-style.css")
        css_file = open(css_path, "r")
        css_str = css_file.read()
        css_file.close()
        style(raw(css_str))

        meta(charset="UTF-8")

    with doc:
        # Header
        h1("image-comparer Similarity Report")

        # Image similarity tables
        for image, similar_images in images.items():
            # Show progress
            reports_generated += 1
            if reports_generated % 10 == 0:
                print('.', end='')

            # Skip unique images
            if len(similar_images) == 0:
                continue

            # Skip sets we've seen before
            comparison_set = list(x[0].path for x in similar_images)
            comparison_set.append(image.path)
            comparison_set.sort()
            comparison_string = "".join(comparison_set)
            if comparison_string in generated_reports:
                continue
            else:
                generated_reports.add(comparison_string)

            with table():
                with tr():
                    th("Thumbnail")
                    th("Path/Last Modified/Hash")
                    th("Delete")

                render_image(image, "Original")

                for similar_image, hash_difference in similar_images:
                    render_image(similar_image, hash_difference)

        # Script output
        div(id='emittedScript')

    report_filename = f'image-comparer-report_{datetime.now().strftime("%Y%m%d%H%M%S")}.html'
    report_file = open(report_filename, 'w', encoding='utf8')
    report_file.write(doc.render())
    report_file.close()

    print()
    print('Done!')
    print(f'Output file is: {report_filename}')

    if len(invalid_paths) > 0:
        print('The following files were not processed:')
        for invalid_path in invalid_paths:
            print(f'    {invalid_path}')


def render_image(image: HashedImage, score):
    with tr():
        # Image
        if image.height > image.width:
            image_style = 'height:200px; width:auto'
        else:
            image_style = 'height:auto; width:200px'

        src = image.path.replace('\\', '/')
        if not src.startswith('/'):
            src = f'/{src}'
        src = f'file://{src}'

        td(img(src=src, style=image_style), style='width:200px;height:200px;text-align:center')

        # Modified date
        last_modified = datetime.fromtimestamp(image.last_modified).strftime("%Y-%m-%d %H:%M:%S")

        # Path/Hash
        with td():
            p(image.path)
            p(f'{image.width} x {image.height}, {last_modified}')
            p(f'Score Difference: {score}')

        # Delete button
        escaped_path = image.path.replace('\\', '&#92;')
        td(button("Delete", onClick=f'addFile(\'{escaped_path}\')'), style='width:100px;text-align:center')


def print_usage():
    print('Image comparer - compares all images in provided folders to find duplicates')
    print('    python image-comparer.py path_to_folder [path_to_folder [path_to_folder...]]')


# Run the program
if __name__ == '__main__':
    main()
