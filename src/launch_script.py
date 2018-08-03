import csv
from tcga import TCGAVariantCaller
import json
import os
import argparse
import csv
from slurm import slurm_submitter

nodes = ["slurm-child1"]
references = ["chr1.fa", "chr2.fa", "chr3.fa", "chr4.fa", "chr5.fa", "chr6.fa", "chr7.fa", "chr8.fa", "chr9.fa", "chr10.fa", "chr11.fa", "chr12.fa", "chr13.fa", "chr14.fa", "chr15.fa", "chr16.fa", "chr17.fa", "chr18.fa", "chr19.fa", "chr20.fa", "chr21.fa", "chr22.fa", "chrX.fa", "chrY.fa", "chrM.fa"]

def extract_matches():
    json_data=open('config.json').read()
    config = json.loads(json_data)

    VAR_INDEX = 0
    VAR_CALLERS = []
    HEADER = []
    MYDIR = os.path.dirname(__file__)
    MYFILE = os.path.join(MYDIR, config["input_file"])
    print(MYDIR)
    with open('full-results-normal.csv', 'rb') as csvfile:
        tcga_reader = csv.reader(csvfile, delimiter=',')
        i = 0
        # This assumes that there is a header in the csv file
        # and that the matches are rows that follow each other
        # TODO: Check to make sure header is proper (i.e. what is being expected)
        for row in tcga_reader:
            if i == 0:
                HEADER = row
                i = i + 1
                continue
            if i % 2 == 1:  # odd - first entry in group
                # create new var caller object
                var_caller = TCGAVariantCaller(VAR_INDEX)

                # Get barcode info
                print(row[3])
                barcode_info = row[3].split('-')

                barcode = barcode_info[0] + "-" + barcode_info[1] + "-" + barcode_info[2]
                var_caller.set_barcode(barcode)

                # Get the tumor / normal type
                if int(barcode_info[3][:2]) < 10:
                    # This is a tumor sample
                    var_caller.set_tumor_gdc_id(row[0])
                    var_caller.set_tumor_file(row[4])
                    var_caller.set_tumor_file_size(row[5])
                    var_caller.set_tumor_platform(row[6])
                    var_caller.set_tumor_file_url(row[7])
                    var_caller.set_tumor_barcode(row[3])
                else:
                    # This is a normal sample
                    var_caller.set_normal_gdc_id(row[0])
                    var_caller.set_normal_file(row[4])
                    var_caller.set_normal_file_size(row[5])
                    var_caller.set_normal_platform(row[6])
                    var_caller.set_normal_file_url(row[7])
                    var_caller.set_normal_barcode(row[3])

                # Get project info
                project_info = row[2].split('-')
                cancer_type = project_info[1]
                var_caller.set_cancer_type(cancer_type)

                VAR_CALLERS.append(var_caller)
            else:
                # Get barcode info
                barcode_info = row[3].split('-')
                
                if int(barcode_info[3][:2]) < 10:
                    # This is a tumor sample
                    VAR_CALLERS[VAR_INDEX].set_tumor_gdc_id(row[0])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file(row[4])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file_size(row[5])
                    VAR_CALLERS[VAR_INDEX].set_tumor_platform(row[6])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file_url(row[7])
                    VAR_CALLERS[VAR_INDEX].set_tumor_barcode(row[3])
                else:
                    # This is a normal sample
                    VAR_CALLERS[VAR_INDEX].set_normal_gdc_id(row[0])
                    VAR_CALLERS[VAR_INDEX].set_normal_file(row[4])
                    VAR_CALLERS[VAR_INDEX].set_normal_file_size(row[5])
                    VAR_CALLERS[VAR_INDEX].set_normal_platform(row[6])
                    VAR_CALLERS[VAR_INDEX].set_normal_file_url(row[7])
                    VAR_CALLERS[VAR_INDEX].set_normal_barcode(row[3])

                #if config["debug"]:
                #    VAR_CALLERS[VAR_INDEX].dump_caller_info()

                # Compare barcodes
                tumor_barcode = barcode_info[0] + "-" + barcode_info[1] + "-" + barcode_info[2]
                normal_barcode_info = VAR_CALLERS[VAR_INDEX].normal_barcode.split('-')
                # print(len(normal_barcode_info))
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


def generate_sbatch_scripts(callers, **kwargs):
    # Generate the sbatch instructions
    node_length = len(nodes)
    node_indx = 0
    wait_id = []
    wait_id.append(-1)
    for caller in callers:
        # For each caller we need to:
        #   1. Download the relevant BAM / BAI files
        #   2. On completion of #1, we need to then launch 25 jobs (Chrom 1 - 22, Y, X, M)
        #       - On completion of each job, the information is copied over to GS bucket and then cleaned up (removed) from node
        #   3. On completion of all jobs, the downloaded files are cleaned up behind

        # working_directory = "/home/torcivia/tcga/{}/".format(caller.barcode)
        # working_directory = "/Users/Jonny/tmp/test_tcga/{}/".format(caller.barcode)
        # WHEN WORKING ON MAC
        #base_directory = "/Users/Jonny/tmp/test_tcga/"
        
        # WORKING ON DESKTOP
        # base_directory = "/Users/Jonny/tmp/test_tcga/"
        
        # IN CLOUD
        #base_directory = "/home/torcivia/tcga/"

        base_directory = kwargs.get("base_dir", "/home/torcivia/tcga/")
        db_address = kwargs.get("ip", "0.0.0.0")

        s = slurm_submitter(base_directory)
        
        # Setup Download
        job_type = "DOWNLOAD"
        node = nodes[node_indx]
        
        s.populate_template(caller, node, job_type, db_address, "download", wait_id[node_indx])
        # print s.template

        # Launch download here
        #job_id = <call for job here>
        job_id = s.launch_job()

        # Set new job type
        job_type = "VARCALL"
        varcall_job_ids = []
        for ref in references:
            s.populate_template(caller, node, job_type, db_address, ref, job_id)
            _job_id = s.launch_job()
            varcall_job_ids.append(_job_id)
        
        # print "VARCALL IDS"
        # print varcall_job_ids

        # Do cleanup
        job_type = "CLEAN"
        s.populate_template(caller, node, job_type, db_address, "cleanup", varcall_job_ids)
        wait_id[node_indx] = s.launch_job()
        
        node_indx += 1
        if node_indx > node_length - 1:
            node_indx = 0
        else:
            wait_id.append(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('ip', help='The IP address of the server, in format xxx.xxx.xxx.xxx.  This is required.')
    parser.add_argument('--base_dir', '-b', dest='base_dir', default='/home/torcivia/tcga/', help='Changes the base directory that computation scripts should be generated.  Default is /home/torcivia/tcga/.')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Turns on verbosity.")
    # parser.add_argument('--quick', '-q', dest='quick', action='store_true', help='Instead of re-generating the pairing index, reads from matches.csv (if exists).')
    parser.add_argument('--matches_log', '-l', dest='log', action='store_true', help='Instead of storing matches as CSV, stores them as LOG file with more detailed output.  This cannot be used as an input for other functionality in this program.')
    args = parser.parse_args()

    callers = []
    try:
        csv_file = open('matches.csv', 'r')
        print "Found matches.csv file"
        csv_reader = csv.reader(csv_file, delimiter=',')
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
            print caller
    except IOError:
        print "matches.csv file doens't appear to exist."
        print "Regenerating matches.csv"
        callers = main()
        # f = open('matches.csv', 'w')
        # if args.log:
        #     for caller in callers:
        #         caller.dump_caller_info(f)
        # else:
        #     for caller in callers:
        #         caller.dump_caller_info_csv(f)
        # f.close()
    
    generate_sbatch_scripts(callers, ip=args.ip, base_dir=args.base_dir)
