#!/usr/bin/python

from support.tcga import TCGAVariantCaller
from support.slurm import slurm_submitter
from server.server import ManagerApplication
import tornado.ioloop
import tornado.httpserver

import json
import argparse
import csv


def extract_matches(config):
    VAR_INDEX = 0
    VAR_CALLERS = []
    with open(config['tcga-sample-list'], 'rb') as csvfile:
        if config['verbose']:
            print("[ debug ] Opening source file {} to ingest tumor / normal pair data.".format(
                config['tcga-sample-list']))
        tcga_reader = csv.reader(csvfile, delimiter=',')
        i = 0
        # This assumes that there is a header in the csv file
        # and that the matches are rows that follow each other
        for row_ in tcga_reader:
            if i == 0:
                # Ignore header
                i = i + 1
                continue
            if i % 2 == 1:  # odd - first entry in group
                # create new var caller object
                var_caller = TCGAVariantCaller(VAR_INDEX)

                # Get barcode info
                print(row_[3])
                barcode_info = row_[3].split('-')

                barcode = barcode_info[0] + "-" + barcode_info[1] + "-" + barcode_info[2]
                var_caller.set_barcode(barcode)

                # Get the tumor / normal type
                if int(barcode_info[3][:2]) < 10:
                    # This is a tumor sample
                    var_caller.set_tumor_gdc_id(row_[0])
                    var_caller.set_tumor_file(row_[4])
                    var_caller.set_tumor_file_size(row_[5])
                    var_caller.set_tumor_platform(row_[6])
                    var_caller.set_tumor_file_url(row_[7])
                    var_caller.set_tumor_barcode(row_[3])
                else:
                    # This is a normal sample
                    var_caller.set_normal_gdc_id(row_[0])
                    var_caller.set_normal_file(row_[4])
                    var_caller.set_normal_file_size(row_[5])
                    var_caller.set_normal_platform(row_[6])
                    var_caller.set_normal_file_url(row_[7])
                    var_caller.set_normal_barcode(row_[3])

                # Get project info
                project_info = row_[2].split('-')
                cancer_type = project_info[1]
                var_caller.set_cancer_type(cancer_type)

                VAR_CALLERS.append(var_caller)
            else:
                # Get barcode info
                barcode_info = row_[3].split('-')

                if int(barcode_info[3][:2]) < 10:
                    # This is a tumor sample
                    VAR_CALLERS[VAR_INDEX].set_tumor_gdc_id(row_[0])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file(row_[4])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file_size(row_[5])
                    VAR_CALLERS[VAR_INDEX].set_tumor_platform(row_[6])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file_url(row_[7])
                    VAR_CALLERS[VAR_INDEX].set_tumor_barcode(row_[3])
                else:
                    # This is a normal sample
                    VAR_CALLERS[VAR_INDEX].set_normal_gdc_id(row_[0])
                    VAR_CALLERS[VAR_INDEX].set_normal_file(row_[4])
                    VAR_CALLERS[VAR_INDEX].set_normal_file_size(row_[5])
                    VAR_CALLERS[VAR_INDEX].set_normal_platform(row_[6])
                    VAR_CALLERS[VAR_INDEX].set_normal_file_url(row_[7])
                    VAR_CALLERS[VAR_INDEX].set_normal_barcode(row_[3])

                if config["debug"]:
                    VAR_CALLERS[VAR_INDEX].dump_caller_info()

                # Compare barcodes
                tumor_barcode = barcode_info[0] + "-" + barcode_info[1] + "-" + barcode_info[2]
                normal_barcode_info = VAR_CALLERS[VAR_INDEX].normal_barcode.split('-')
                normal_barcode = normal_barcode_info[0] + "-" + normal_barcode_info[1] + "-" + normal_barcode_info[2]
                if tumor_barcode == normal_barcode:
                    pass
                else:
                    print("No Match")
                # Increase the variant caller index
                VAR_INDEX += 1
            # increase the row index
            i = i + 1
    # Return the variant callers to the calling function
    return VAR_CALLERS


class BatchScriptor:
    def __init__(self, callers_, config, **kwargs):
        self.callers = callers_
        self.config = config
        self.base_directory = kwargs.get("base_dir", "./")
        self.db_address = kwargs.get("ip", "127.0.0.1:8081")
        self.nodes = self.config['nodes']
        self.references = self.config['references']
        self.node_length = len(self.nodes)
        self.node_indx = 0
        self.wait_id = []
        for x in range(0, self.node_length):
            self.wait_id.append(-1)

    def generate_sbatch_by_tcga_id(self, tcga_id):
        for caller_ in self.callers:
            if caller_.barcode == tcga_id:
                print("Matched, submitting job.")
                return self.generate_sbatch_script(caller_)
        return False

    def generate_sbatch_scripts(self):
        for caller_ in self.callers:
            self.generate_sbatch_script(caller_)

    def generate_sbatch_script(self, caller_):
        # Generate the sbatch instructions

        # for caller_ in self.callers:
        # For each caller we need to:
        #   1. Download the relevant BAM / BAI files
        #   2. On completion of #1, we need to then launch 25 jobs (Chrom 1 - 22, Y, X, M)
        #       - On completion of each job, the information is copied over to GS bucket and
        #       then cleaned up (removed) from node
        #   3. On completion of all jobs, the downloaded files are cleaned up behind

        s = slurm_submitter(self.base_directory)

        # Setup Download
        job_type = "DOWNLOAD"
        node = self.nodes[self.node_indx]

        s.populate_template(caller_, node, job_type, self.db_address, "download", self.wait_id[self.node_indx])
        # print s.template

        # Launch download here
        # job_id = <call for job here>
        job_id = s.launch_job()

        # Set new job type
        job_type = "VARCALL"
        varcall_job_ids = []
        for ref in self.references:
            s.populate_template(caller_, node, job_type, self.db_address, ref, job_id)
            _job_id = s.launch_job()
            varcall_job_ids.append(_job_id)

        # Do cleanup
        job_type = "CLEAN"
        s.populate_template(caller_, node, job_type, self.db_address, "cleanup", varcall_job_ids)
        self.wait_id[self.node_indx] = s.launch_job()

        self.node_indx += 1
        if self.node_indx > self.node_length - 1:
            self.node_indx = 0
        # else:
        #    wait_id.append(-1)

        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('ip', help='The IP address of the server, in format xxx.xxx.xxx.xxx.  This is required.')
    parser.add_argument('--base_dir', '-b', dest='base_dir', default='./',
                        help='Changes the base directory that computation scripts should be generated.  Default is '
                             './ (the current directory).  This directory should be where the data will be transferred'
                             ' to and manipulated on the node.')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Turns on verbosity.")
    parser.add_argument('--bypass_server', dest='bypass_server', action='store_true', help="Turns off server and just "
                                                                                    "submits jobs.")

    parser.add_argument('--matches_log', '-l', dest='log', action='store_true', help='Instead of storing matches as '
                                                                                     'CSV, stores them as LOG file '
                                                                                     'with more detailed output.  '
                                                                                     'This cannot be used as an input '
                                                                                     'for other functionality in this '
                                                                                     'program.')
    parser.add_argument('--config', '-c', dest='config', default='src/configuration.json', help='Configuration file '
                                                                                                'which '
                                                                                                'lists the nodes and '
                                                                                                'the '
                                                                                                'references used.  See '
                                                                                                'configuration.json '
                                                                                                'as an '
                                                                                                'example.')

    args = parser.parse_args()

    with open(args.config, 'r') as fh:
        configuration = json.load(fh)

    callers = []
    try:
        csv_file = open(configuration['input_file'], 'r')
        print("Found {} file".format(configuration['input_file']))
        csv_reader = csv.reader(csv_file, delimiter=',')
        if configuration["header"]:
            next(csv_reader)
        indx = 1
        for row in csv_reader:
            caller = TCGAVariantCaller(indx)
            caller.set_index(indx)
            caller.set_barcode(row[1])
            caller.set_tumor_barcode(row[2])
            caller.set_tumor_file(row[3])
            caller.set_tumor_gdc_id(row[4])
            caller.set_tumor_file_url(row[5])
            caller.set_tumor_file_size(row[6])
            caller.set_tumor_platform(row[7])
            caller.set_normal_barcode(row[8])
            caller.set_normal_file(row[9])
            caller.set_normal_gdc_id(row[10])
            caller.set_normal_file_url(row[11])
            caller.set_normal_file_size(row[12])
            caller.set_normal_platform(row[13])
            caller.set_cancer_type(row[14])
            caller.set_total_size(row[15])
            callers.append(caller)
            indx += 1
            if args.verbose:
                print(caller)
    except IOError:
        print("{} file does not appear to exist.".format(configuration['input_file']))
        print("Generating {}".format(configuration['input_file']))
        callers = extract_matches(configuration)
        f = open(configuration['input_file'], 'w')
        if args.log:
            for caller in callers:
                caller.dump_caller_info(f)
        else:
            for caller in callers:
                caller.dump_caller_info_csv(f)
        f.close()

    batch_scriptor = BatchScriptor(callers, configuration, ip=args.ip, base_dir=args.base_dir)
    if args.bypass_server:
        batch_scriptor.generate_sbatch_scripts()
        # generate_sbatch_scripts(callers, configuration, ip=args.ip, base_dir=args.base_dir, )
    else:
        settings = {}
        http_server = tornado.httpserver.HTTPServer(ManagerApplication(callers, batch_scriptor))
        http_server.listen(8081)
        tornado.ioloop.IOLoop.instance().start()
