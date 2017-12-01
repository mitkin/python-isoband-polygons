import logging
import argparse


def parse_arguments(arguments=None):
    """
    Parse and run the arguments
    :param arguments: an arguments list or None to parse all
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file",
                        type=argparse.FileType('r'))
    return parser


def main():
    logger = logging.getLogger(__name__)
    parser = parse_arguments()
