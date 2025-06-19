import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--strategy', type=str, required=True)
    return parser.parse_args()
