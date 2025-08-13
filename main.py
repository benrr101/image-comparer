import dominate
import imagehash
import os
import sys
import time

from PIL import Image, ImageFile
from datetime import datetime, timedelta
from dominate.tags import *
from dominate.util import raw

ImageFile.LOAD_TRUNCATED_IMAGES = True
HASHING_ALGORITHM = imagehash.average_hash
HASH_SIZE = 32
THRESHOLD = 10


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


def print_usage():
    print('Image comparer - compares all images in provided folders to find duplicates')
    print('    python image-comparer.py path_to_folder [path_to_folder ...]')


def render_image(image: HashedImage):
    with tr():
        # Image
        if image.height > image.width:
            image_class = 'fixedHeight'
        else:
            image_class = 'fixedWidth'

        src = image.path.replace('\\', '/')
        if not src.startswith('/'):
            src = f'/{src}'
        src = f'file://{src}'

        td(img(src=src, className=image_class), className='imgtd')

        # Modified date
        last_modified = datetime.fromtimestamp(image.last_modified).strftime("%Y-%m-%d %H:%M:%S")

        # Path/Hash
        with td():
            p(image.path)
            p(f'{image.width} x {image.height}, {last_modified}')

        # Delete button
        escaped_path = image.path.replace('\\', '&#92;')
        td(button("Delete", onClick=f'addFile(\'{escaped_path}\', this);'), className='buttontd')


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
    print('--- Discovering Images', end='')
    discovery_start = time.time()

    images = []
    invalid_paths = []
    images_discovered = 0
    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                image_path = os.path.join(root, file)
                try:
                    # Add image to bucket of images
                    image = HashedImage(image_path)
                    images.append(image)

                    # Show progress
                    images_discovered += 1
                    if images_discovered  % 100 == 0:
                        print('.', end='')

                except Exception as e:
                    if hasattr(e, 'message'):
                        invalid_paths.append(f"{image_path} : {e.message}")
                    else:
                        invalid_paths.append(f"{image_path} : {e}")

    discovery_end = time.time()
    print()
    print(f"--! Discovered Images: {images_discovered}, {str(timedelta(seconds=round(discovery_end - discovery_start, 3)))}")

    # Step 3: Find similar files based on hash
    print('--- Comparing Images', end='')
    comparison_start = time.time()

    comparisons_made = 0
    image_buckets = []
    while len(images) > 0:
        # Pull image off top of stack and create bucket for similar images
        image_a = images.pop()
        image_bucket = []

        # Compare with all the images
        for image_b in images:
            # Don't compare the image to itself
            if image_a == image_b:
                continue

            # Compute the difference
            hash_difference = image_a.hash - image_b.hash
            if hash_difference <= THRESHOLD:
                image_bucket.append(image_b)

            # Show progress
            comparisons_made += 1
            if comparisons_made % 10000 == 0:
                print('.', end='')

        # Remove bucket from the image set
        for image in image_bucket:
            images.remove(image)

        # Add the first image back to its bucket
        image_bucket.append(image_a)

        # Add bucket to list
        image_buckets.append(image_bucket)

    comparison_end = time.time()
    print()
    print(f"--! Compared Images: {comparisons_made}, {str(timedelta(seconds=round(comparison_end - comparison_start, 3)))}")

    # Step 4: Generate report
    print()
    print('--- Generating Report', end='')
    report_start = time.time()

    reports_generated = 0
    doc = dominate.document(title='image-comparer report', )

    # Render header
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

    # Render body
    with doc:
        # Header
        h1("image-comparer Similarity Report")

        # Image similarity tables
        for image_bucket in image_buckets:
            # Skip unique images (ie, only itself in its bucket)
            if len(image_bucket) == 1:
                continue

            # Generate table for the bucket
            with table():
                with tr():
                    th("Thumbnail")
                    th("Path/Last Modified")
                    th("Delete")

                for image in image_bucket:
                    render_image(image)

        # Script output
        div(id='emittedScript')

        # Show progress
        reports_generated += 1
        if reports_generated % 10 == 0:
            print('.', end='')

    report_filename = f'image-comparer-report_{datetime.now().strftime("%Y%m%d%H%M%S")}.html'
    report_file = open(report_filename, 'w', encoding='utf8')
    report_file.write(doc.render())
    report_file.close()

    report_end = time.time()
    print()
    print(f"--! Generated Report: {reports_generated}, {str(timedelta(seconds=round(report_end - report_start, 3)))}")

    print()
    print("------------------")
    print(f'Output file is: {report_filename}')
    if len(invalid_paths) > 0:
        print('The following files were not processed:')
        for invalid_path in invalid_paths:
            print(f'    {invalid_path}')

# Run the program
if __name__ == '__main__':
    main()
