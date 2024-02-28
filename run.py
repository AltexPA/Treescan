#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
'''
import argparse
import sys
import os

from jinja2 import Environment, FileSystemLoader

def index_to_text(path_to_scan):
    # Create a text file in the directory to index
    index_file_path = os.path.join(path_to_scan, 'index.txt')
    with open(index_file_path, 'w') as output_file:
        # Walk the directory and write the content to the file
        for root, dirs, files in os.walk(path_to_scan):
            print(root)
            print(dirs)
            for dir in dirs:
                print(os.path.join(root, dir))
            print('---')
            path = root.split(os.sep)
            output_file.write((len(path) - 1) * '---' + os.path.basename(root) + '\n')
            for file in files:
                output_file.write(len(path) * '---' + file + '\n')


def stats(path_to_scan):
    stats = {}

    # Walk the directory and count the number of files and directories
    for root, dirs, files in os.walk(path_to_scan, topdown=False):
        stats[root] = {}
        stats[root]['nb_files'] = len(files)
        
        # get total size of files in the directory
        directory_size = 0
        for file in files:
            directory_size += os.path.getsize(os.path.join(root, file))
        stats[root]['size'] = directory_size

        # cumulate the number of files, and size in subdirectories. Notice that we use the topdown=False option
        if len(dirs) > 0:
            total_files_in_subdirs = 0
            total_size_in_subdirs = 0
            for dir in dirs:
                total_files_in_subdirs += stats[os.path.join(root, dir)]['total_nb_files']
                total_size_in_subdirs += stats[os.path.join(root, dir)]['total_size']
            stats[root]['total_nb_files'] = total_files_in_subdirs + len(files)
            stats[root]['total_size'] = total_size_in_subdirs + directory_size

            # Memorize subdirectories at this level and make percentage of each own size
            stats[root]['subdirs'] = []
            for dir in dirs:
                stats[root]['subdirs'].append(
                    {'name': dir,
                    'percentage': stats[os.path.join(root, dir)]['total_size'] / total_size_in_subdirs * 100
                    }
                )
            
        else:
            # No subdirectories, just copy the values
            stats[root]['total_nb_files'] = len(files)
            stats[root]['total_size'] = directory_size
            stats[root]['subdirs'] = []

    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='TreeScan',
        description='Tools to index and display directory stats'
    )
    parser.add_argument('path', help='Path to the directory to index or display stats')
    parser.add_argument('-i', '--index', action='store_true', help='Index the directory')
    parser.add_argument('-s', '--stats', action='store_true', help='Display directory stats')
    args = parser.parse_args()

    # Test if the path exists
    if not os.path.exists(args.path):
        print('The path does not exist')
        sys.exit(1)

    if args.index:
        # Code for indexing the directory
        index_to_text(args.path)

    if args.stats:
        # Calculate stats
        stats = stats(args.path)

        # Create a Jinja2 environment
        env = Environment(loader=FileSystemLoader('templates/'))
        template = env.get_template('stats.html')

        # Prepare datas to be rendered
        datas = {
            'root': args.path,
            'nb_files': stats[args.path]['nb_files'],
            'total_nb_files': stats[args.path]['total_nb_files'],
            'total_size': stats[args.path]['total_size'] // 1024,
            'subdirs': []
        }
        for subdir in stats[args.path]['subdirs']:
            datas['subdirs'].append(
                {
                    'name': subdir['name'],
                    'percentage': '%d' % subdir['percentage'],
                    'size': stats[os.path.join(args.path, subdir['name'])]['total_size'] // 1024
                }
            )
        

        # Render the template with the stats
        output = template.render(datas=datas)
        print(stats[args.path])
        print(output)
        # Write the output to a file
        with open('stats.html', 'w') as output_file:
            output_file.write(output)

        # for root, stat in stats.items():
        #     print(f'Path: {root}')
        #     print(f'Number of files: {stat["nb_files"]}')
        #     print(f'Size: {stat["size"]}')
        #     print(f'Total number of files: {stat["total_nb_files"]}')
        #     print(f'Total size of files: {stat["total_size"]/1024:.2f} KB')
        #     print('Subdirectories:')
        #     for subdir in stat['subdirs']:
        #         print(f'    {subdir["name"]}: {subdir["percentage"]:.2f}%')
        #     print('---')