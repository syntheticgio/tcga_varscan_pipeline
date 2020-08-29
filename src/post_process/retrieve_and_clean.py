from google.cloud import storage
import argparse


class StorageHandler:
    def __init__(self, prog_args):
        self.client = storage.Client()

        # Set staging location
        self.staging_directory = prog_args.staging_directory

        # Arguments for retrieving bucket details
        self.bucket_args = {
            "delimiter": prog_args.delimiter,
            "prefix": prog_args.prefix,
            "name": prog_args.bucket
        }
        self.bucket = self.client.get_bucket(self.bucket_args["name"])

        # TCGA IDs found in the bucket
        self.directories = []

        # List of all files within the bucket / prefix / delimiter settings
        self.blobs = None

        if args.regen_dirs:
            print("Regenerating directory list... may take a while.")
            self.retrieve_directory_list()
        else:
            try:
                with open("directories.txt", "r") as f:
                    for line in f:
                        self.directories.append(line.strip())
            except IOError:
                print("Regenerating directory list... may take a while.")
                self.retrieve_directory_list()

    def retrieve_directory_list(self):

        self.blobs = self.client.list_blobs(self.bucket_args["name"],
                                            prefix=self.bucket_args["prefix"],
                                            delimiter=self.bucket_args["delimiter"])
        split_num = len(self.bucket_args["prefix"].split("/")) - 1
        dup = {}
        for blob in self.blobs:
            tcga_id = blob.name.split("/")[split_num]
            if tcga_id not in dup:
                self.directories.append(tcga_id)
                dup[tcga_id] = len(self.directories) - 1
        with open("directory_list.txt", "w") as f:
            for d in self.directories:
                f.write("{}\n".format(d))

    def download_variant_calls(self):
        pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('staging_directory',
                        help='Where the files should be staged at.  This should be either an absolute path or '
                             'relative to the run directory.')
    parser.add_argument('--verbose', '-v',
                        dest='verbose',
                        action='store_true',
                        help="Turns on verbosity.")
    parser.add_argument('--regen_dirs', '-r',
                        dest='regen_dirs',
                        action='store_true',
                        help="Regenerates the directories from the cloud bucket (takes a while).")
    parser.add_argument('--prefix', '-p',
                        dest='prefix',
                        default='tcga_wgs_results/',
                        help='Google cloud bucket prefix.  " \
                        "In order to get all files and parse directories with TCGA IDs.')
    parser.add_argument('--delimiter', '-d',
                        dest='delimiter',
                        default=None,
                        help='Google cloud bucket delimiter.')
    parser.add_argument('--bucket', '-b',
                        dest='bucket',
                        default='iron-eye-6998',
                        help='Google cloud bucket id.')

    args = parser.parse_args()

    # Set up storage handler
    sh = StorageHandler(args)
    print("Number of directories to process: {}".format(len(sh.directories)))

    # Begin to download the appropriate files
