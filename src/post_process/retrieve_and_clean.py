from google.cloud import storage
import argparse





class StorageHandler:
    def __init__(self, args):
        self.client = storage.Client()
        self.bucket_name = args.bucket
        self.bucket = self.client.get_bucket(self.bucket_name)
        self.directories = []
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

        print("Initialized {} number of directories.".format(len(self.directories)))

    def retrieve_directory_list(self):
        self.blobs = self.client.list_blobs(args.bucket, prefix="tcga_wgs_results/")
        dup = {}
        for blob in self.blobs:
            tcga_id = blob.name.split("/")[1]
            if tcga_id not in dup:
                self.directories.append(tcga_id)
                dup[tcga_id] = len(self.directories) - 1
        with open("directory_list.txt", "w") as f:
            for d in self.directories:
                f.write("{}\n".format(d))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('--verbose', '-v',
                        dest='verbose',
                        action='store_true',
                        help="Turns on verbosity.")
    parser.add_argument('--bucket', '-b',
                        dest='bucket',
                        default='iron-eye-6998',
                        help='Google cloud bucket id.')

    args = parser.parse_args()
    main(args)
