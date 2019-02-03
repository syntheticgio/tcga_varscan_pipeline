#!/usr/bin/python

# This script takes in a VCF file and outputs a matrix
# as expected by the qqman package in R


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('ip', help='The IP address of the server, in format xxx.xxx.xxx.xxx.  This is required.')
    parser.add_argument('--base_dir', '-b', dest='base_dir', default='/home/torcivia/tcga/', help='Changes the base directory that computation scripts should be generated.  Default is /home/torcivia/tcga/.')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Turns on verbosity.")
    # parser.add_argument('--quick', '-q', dest='quick', action='store_true', help='Instead of re-generating the pairing index, reads from matches.csv (if exists).')
    parser.add_argument('--matches_log', '-l', dest='log', action='store_true', help='Instead of storing matches as CSV, stores them as LOG file with more detailed output.  This cannot be used as an input for other functionality in this program.')
    args = parser.parse_args()