import argparse
from folder_analyzer import MusicFolder


parser = argparse.ArgumentParser(description='Process and add metadata to your music folders.')
parser.add_argument('--path', '-p', type=str, required=True,
                    help='the path of the music folder')
args = parser.parse_args()
a = MusicFolder(args.path)