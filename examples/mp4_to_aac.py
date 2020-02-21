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
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '--mp4-file',
        dest='mp4_file',
        required=True,
        type=str,
        help='mp4 file to extract aac data from.')

    parser.add_argument(
        '--track-id',
        dest='track_id',
        required=True,
        type=int,
        help='the ID of the aac track.')

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

    with open(args.mp4_file, 'rb') as input_file:
        mp4_data = input_file.read()

    extractor.open(mp4_data, args.track_id)

    aac_file = open(args.output_file, 'wb')

    while not extractor.at_end():
        aac_file.write(extractor.adts_header())
        aac_file.write(extractor.sample_data())

        extractor.advance()

    extractor.close()
    aac_file.close()


if __name__ == '__main__':
    main()
