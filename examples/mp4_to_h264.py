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


def read_nalu_size(data, length_size):
    """Read nalu size."""
    result = 0
    for i in range(length_size):
        result |= ord(data[i]) << ((length_size - 1) - i) * 8
    return result


def main():
    """Example showing how to extract h264 data."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        '--mp4-file',
        dest='mp4_file',
        required=True,
        type=str,
        help='mp4 file to extract h264 data from.')

    parser.add_argument(
        '--out',
        dest='output_file',
        default='out.h264',
        type=str,
        help='file to write the extract h264 data to.')

    if '--dry-run' in sys.argv:
        return

    args = parser.parse_args()

    extractor = petro.AVCSampleExtractor()
    extractor.set_file_path(args.mp4_file)
    if not extractor.open():
        print("Unable to open {}".format(args.mp4_file))
        return

    h264_file = open(args.output_file, 'wb')
    start_code = '\x00\x00\x00\x01'

    h264_file.write(start_code)
    h264_file.write(extractor.sps())
    h264_file.write(start_code)
    h264_file.write(extractor.pps())

    nalu_length_size = extractor.nalu_length_size()
    while not extractor.at_end():
        sample = extractor.sample_data()
        sample_size = extractor.sample_size()
        offset = 0
        while offset < sample_size:
            nalu_size = read_nalu_size(sample[offset:], nalu_length_size)
            offset += nalu_length_size

            nalu_sample = sample[offset:offset + nalu_size]
            h264_file.write(start_code)
            h264_file.write(nalu_sample)
            offset += nalu_size

        extractor.advance()

    extractor.close()
    h264_file.close()


if __name__ == '__main__':
    main()
