#! /usr/bin/env python
# encoding: utf-8

"""
Petro Python unit tests.

Copyright (c) Steinwurf ApS 2016.
All Rights Reserved

Distributed under the "BSD License". See the accompanying LICENSE.rst file.
"""

import unittest
import petro
import os


class TestVersion(unittest.TestCase):
    """Version test."""

    def test_version(self):
        """Test version."""
        versions = petro.__version__.split('\n')
        for version in versions:
            # Make sure that a version number is available for all
            # dependencies.
            self.assertNotEqual(
                version.split(':')[1].strip(), '', msg=version.strip())


class TestExtractH264(unittest.TestCase):
    """H264 extraction test."""

    def test_extraction(self):
        """Test extraction."""
        h264_file_path = os.path.join('test', 'test1.h264')
        h264_file = open(h264_file_path, 'rb')

        extractor = petro.AVCSampleExtractor()
        mp4_file_path = os.path.join('test', 'test1.mp4')
        with open(mp4_file_path, 'rb') as mp4_file:
            mp4_data = mp4_file.read()

        # The track id of the test file's h264 trak is 1
        extractor.open(mp4_data, 1)

        self.check_sample(h264_file, extractor.sps())
        self.check_sample(h264_file, extractor.pps())

        nalu_length_size = extractor.nalu_length_size()

        self.assertFalse(extractor.at_end())
        while not extractor.at_end():

            sample = extractor.sample_data()
            sample_size = extractor.sample_size()
            offset = 0
            while offset < sample_size:
                nalu_size =\
                    self.read_nalu_size(sample[offset:], nalu_length_size)
                offset += nalu_length_size
                self.check_sample(h264_file, sample[offset:offset + nalu_size])
                offset += nalu_size

            extractor.advance()

        extractor.close()
        h264_file.close()

    def check_sample(self, h264_file, sample):
        """Compare sample with sample extracted from h264 file."""
        # skip nalu start codes
        h264_file.seek(h264_file.tell() + 4)
        expected_sample = h264_file.read(len(sample))
        self.assertEqual(expected_sample, sample)

    def read_nalu_size(self, data, length_size):
        """Read nalu size."""
        result = 0
        for i in range(length_size):
            v = data[i]
            if type(v) == str:
                v = ord(v)
            result |= v << ((length_size - 1) - i) * 8
        return result


class TestExtractAAC(unittest.TestCase):
    """AAC extraction test."""

    def test_extraction(self):
        """Test extraction."""
        aac_file_path = os.path.join('test', 'test1.aac')
        aac_file = open(aac_file_path, 'rb')

        extractor = petro.AACSampleExtractor()
        mp4_file_path = os.path.join('test', 'test1.mp4')
        with open(mp4_file_path, 'rb') as mp4_file:
            mp4_data = mp4_file.read()

        # The track id of the test file's aac trak is 2
        extractor.open(mp4_data, 2)

        self.assertFalse(extractor.at_end())
        while not extractor.at_end():
            adts_header = extractor.adts_header()
            self.check_sample(aac_file, adts_header)

            sample = extractor.sample_data()
            self.check_sample(aac_file, sample)

            extractor.advance()

        extractor.close()
        aac_file.close()

    def check_sample(self, aac_file, sample):
        """Compare sample with sample extracted from aac file."""
        expected_sample = aac_file.read(len(sample))
        self.assertEqual(expected_sample, sample)


def main():
    """Main function."""
    unittest.main()


if __name__ == "__main__":
    main()
