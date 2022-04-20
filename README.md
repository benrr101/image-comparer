# `image-comparer`
A quick and dirty script using `imagehash` for comparing a collection of folders to find duplicates. Written in an evening.

## Usage
Create a virtual environment and `pip install` the requirements
```shell
> python main.py folder_path [2nd_folder_path[ 3rd_folder_path[...]]]
```
`folder_path` is a path to a folder with images, more than one may be provided. Images in subfolders are compared,
as well.

## Output
After the script runs, a html report will be written to the working directory. I wrote this script so I could
easily find duplicate images, I made sure the report gives pertinent information to make a decision on which files to
keep. The report shows a thumbnail of the similar images, file paths, date/time modified, hash difference, and
for each image, a "delete" button. This button does not delete the file, but appends it to a list at the bottom of
the report that can be copy/pasted as a deletion script. Very quick and dirty, but it worked for my needs.

## Configuration
There's very little configuration points in this quick and dirty script. Edit the constants in `main.py` to change
config:
* `HASHING_ALGORITHM` - The algorithm to use to hash the images for comparison, see [`imagehash` docs](https://github.com/JohannesBuchner/imagehash#example-1-icon-dataset)
* `HASH_SIZE` - Size of the hash to calculate, see [`imagehash` docs](https://github.com/JohannesBuchner/imagehash#example-1-icon-dataset)
* `THRESHOLD` - Hash differences above this value will not be considered 'similar'. Values between 10 and 100 give 
                reasonable results.