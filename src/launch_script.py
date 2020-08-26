#!/usr/bin/python

from support.tcga import TCGAVariantCaller
from support.slurm import slurm_submitter
from server.server import ManagerApplication
import tornado.ioloop
import tornado.httpserver

import json
import argparse
import csv
import socket
from requests import get
import subprocess


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
        self.output_bucket = self.config['output_bucket']
        self.node_length = len(self.nodes)
        self.node_indx = 0
        self.wait_id = []
        for x in range(0, self.node_length):
            self.wait_id.append(-1)
        self.sample_id_lists = {}
        self.s = slurm_submitter(self.base_directory, self.output_bucket)

    @staticmethod
    def run_test(config):
        s = slurm_submitter(config["base_directory"])
        # Setup Download
        job_type = "TEST"
        nodes = []
        try:
            nodes = config['nodes']
        except KeyError:
            print("[ error ] 'nodes' field must be provided in config file to specify which slurm nodes (by name) are "
                  "available.")
            exit(1)
        assert len(nodes) > 0
        node = nodes[0]

        s.populate_template(None, node, job_type, None)

        # Launch test here
        # job_id = <call for job here>
        job_id = s.launch_job()

    def generate_sbatch_by_tcga_id(self, tcga_id):
        # TODO: Might need to remove the caller from the self.callers if successful
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

        # s = slurm_submitter(self.base_directory)

        # Setup Download
        job_type = "DOWNLOAD"
        node = self.nodes[self.node_indx]  # node is slurm-child3 - for example

        self.s.populate_template(caller_, node, job_type, self.db_address, "download", self.wait_id[self.node_indx])
        print("  -- New job submitted; waiting on job {} to begin.".format(self.wait_id[self.node_indx]))
        # print s.template

        # Launch download here
        # job_id = <call for job here>
        job_id = self.s.launch_job()
        self.sample_id_lists[caller_.barcode] = {}
        self.sample_id_lists[caller_.barcode][job_type] = job_id

        # Set new job type
        job_type = "VARCALL"
        varcall_job_ids = []
        for ref in self.references:
            self.s.populate_template(caller_, node, job_type, self.db_address, ref, job_id)
            _job_id = self.s.launch_job()
            varcall_job_ids.append(_job_id)
        self.sample_id_lists[caller_.barcode][job_type] = varcall_job_ids

        # Do cleanup
        job_type = "CLEAN"
        self.s.populate_template(caller_, node, job_type, self.db_address, "cleanup", varcall_job_ids)
        self.wait_id[self.node_indx] = self.s.launch_job()
        self.sample_id_lists[caller_.barcode][job_type] = self.wait_id[self.node_indx]

        self.node_indx += 1
        if self.node_indx > self.node_length - 1:
            self.node_indx = 0
        # else:
        #    wait_id.append(-1)

        return True


if __name__ == "__main__":
    def port(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError("%s is less than 0. Ports must be between 0 and 65535")
        if ivalue > 65535:
            raise argparse.ArgumentTypeError("%s is greater than 65535. Ports must be between 0 and 65535")
        return ivalue


    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('--ip', '-i',
                        help='The IP address (and port) of the server, in format xxx.xxx.xxx.xxx.  If not specified '
                             'the program will try to generate it.')
    parser.add_argument('--port', '-p',
                        type=port,
                        default=8081,
                        help='The port of the server, If not specified '
                             'the default of 8081 is used.')
    parser.add_argument('--verbose', '-v',
                        dest='verbose',
                        action='store_true',
                        help="Turns on verbosity.")
    parser.add_argument('--bypass_server',
                        dest='bypass_server',
                        action='store_true',
                        help="Turns off server and just submits jobs.")
    parser.add_argument('--config', '-c',
                        dest='config',
                        default='src/configuration.json',
                        help='Configuration file which lists the nodes and the references used.  See '
                             'configuration.json as an example.')
    parser.add_argument('--test', '-t',
                        dest='test',
                        action='store_true',
                        help="Runs test and exits.")

    args = parser.parse_args()

    with open(args.config, 'r') as fh:
        configuration = json.load(fh)
        # TODO: Need to make sure everything needed is specified with a error message if not

    if args.test:
        # Run test and exit
        BatchScriptor.run_test(configuration)
        print("Launched test: exiting program.  Use SQUEUE to see results or examine the output files in the working "
              "directory {} on the node being used {}.".format(
            configuration["base_directory"],
            configuration["nodes"][0])
        )
        exit(0)

    if not args.ip:
        if args.bypass_server:
            print("[ error ] The IP address will need to be set if not running locally!")
            exit(0)
        # getting the hostname by socket.gethostname() method
        hostname = socket.gethostname()
        # getting the IP address using socket.gethostbyname() method
        ip_address = socket.gethostbyname(hostname)
        print("Setting the host to: {}:{} (the current master node)".format(ip_address, args.port))
        args.ip = "{}:{}".format(ip_address, args.port)
    else:
        print("Using {}:{} for the server IP and port.".format(args.ip, args.port))
        print("NOTE: If this does not include the port, this will not work unless the port is on 80!  (This is not "
              "the default, the default port is 8081 and the ip and port should be specified as follows <ip "
              "address>:<port>.")

    if not args.bypass_server:
        # Get external IP address for javascript
        external_ip = get('https://api.ipify.org').text
        # Replace in javascript
        # subprocess.run(
        #     ["sed -i -e 's/REPLACE_URL_HERE/{}:{}/g' server/static/update.js".format(external_ip, args.port)],
        #     shell=True)

    # Get finished matches as to not run those...
    match_list = []
    try:
        with open(configuration['completed_list'], "r") as f:
            matches_reader = csv.reader(f, delimiter=",")
            for row in matches_reader:
                match_list.append(row[0])
    except IOError:
        print("Couldn't get the previous finished matches!")
    callers = []
    try:
        csv_file = open(configuration['input_file'], 'r')
        print("Found {} file".format(configuration['input_file']))
        csv_reader = csv.reader(csv_file, delimiter=',')
        if configuration["header"]:
            next(csv_reader)
        indx = 1
        matched_num = 0
        new_num = 0
        for row in csv_reader:
            mtch = False
            for match in match_list:
                if match == row[1]:
                    if args.verbose:
                        print("There was a match of {} .... skipping.".format(match))
                    mtch = True
                    matched_num += 1
                    break
            if mtch:
                continue
            new_num += 1
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
        print("Matched entries: {}".format(matched_num))
        print("New entries: {}".format(new_num))
    except IOError:
        print("{} file does not appear to exist.".format(configuration['input_file']))
        print("Generating {}".format(configuration['input_file']))
        callers = extract_matches(configuration)
        with open(configuration['input_file'], 'w') as f:
            for caller in callers:
                caller.dump_caller_info_csv(f)

    batch_scriptor = BatchScriptor(callers, configuration, ip=args.ip, base_dir=configuration["base_directory"])
    if args.bypass_server:
        batch_scriptor.generate_sbatch_scripts()
        # generate_sbatch_scripts(callers, configuration, ip=args.ip, base_dir=args.base_dir, )
    else:
        settings = {}
        http_server = tornado.httpserver.HTTPServer(ManagerApplication(callers, batch_scriptor))
        try:
            http_server.listen(args.port)
        except BaseException as e:
            print("[ error ] could not open on port %s because of error: %s", str(args.port), e)
            print("Failed to open server.  Aborting program.")
            exit(2)
        tornado.ioloop.IOLoop.instance().start()
