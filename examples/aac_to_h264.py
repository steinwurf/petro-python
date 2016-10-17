#! /usr/bin/env python
# encoding: utf-8

"""
Petro Python unit tests.

Copyright (c) Steinwurf ApS 2016.
All Rights Reserved

Distributed under the "BSD License". See the accompanying LICENSE.rst file.
"""
import argparse
import petro
import sys


def main():
    """Example showing how to extract aac data."""
    sys.argv.append('--mp4-file=../test/test1.mp4')
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '--mp4-file',
        dest='mp4_file',
        required=True,
        type=str,
        help='mp4 file to extract aac data from.')

    parser.add_argument(
        '--out',
        dest='output_file',
        default='out.aac',
        type=str,
        help='file to write the extract aac data to.')

    if '--dry-run' in sys.argv:
        return

    args = parser.parse_args()

    extractor = petro.AACSampleExtractor()
    extractor.set_file_path(args.mp4_file)
    if not extractor.open():
        print("Unable to open {}".format(args.mp4_file))
        return

    aac_file = open(args.output_file, 'wb')

    while not extractor.at_end():
        aac_file.write(extractor.adts_header())
        aac_file.write(extractor.sample_data())

        extractor.advance()

    extractor.close()
    aac_file.close()


if __name__ == '__main__':
    main()
