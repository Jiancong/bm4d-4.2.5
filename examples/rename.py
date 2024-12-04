import os

for filename in os.listdir('.'):
    filepath = os.path.join('.', filename)

    if os.path.isfile(filepath):
        new_filename = filename.replace(' ', '_')
        new_filepath = os.path.join('.', new_filename)

        os.rename(filepath, new_filepath)

