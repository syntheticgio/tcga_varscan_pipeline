import csv
from tcga import TCGAVariantCaller
import json
import os
import argparse
<<<<<<< Updated upstream
import csv
=======
>>>>>>> Stashed changes


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


<<<<<<< Updated upstream
def generate_sbatch_scripts(callers):
    # Generate the sbatch instructions
    for caller in callers:
        # For each caller we need to:
        #   1. Download the relevant BAM / BAI files
        #   2. On completion of #1, we need to then launch 25 jobs (Chrom 1 - 22, Y, X, M)
        #       - On completion of each job, the information is copied over to GS bucket and then cleaned up (removed) from node
        #   3. On completion of all jobs, the downloaded files are cleaned up behind
        #
        #  SAMPLE SBATCH
        #   #!/bin/bash
        #   #
        #   #SBATCH --job-name=<TCGA>_<CHR> (or DOWNLOAD or CLEAN)
        #   #SBATCH --output=<TCGA>_%A_<CHR>.stout
        #   #SBATCH --error=<TCGA>_%A_<CHR>.sterr
        #   #
        #   #SBATCH --mail-type=FAIL,END
        #   #SBATCH --mail-user=torcivia@gwu.edu
        #   #
        #   #SBATCH --nodelist=<node name>
        #   #
        #   #SBATCH --ntasks=1
        #   #SBATCH --mem=1024
        #   #SBATCH --dependency=afterok:<job id>
        #   #SBATCH --chdir=<working directory>
        #
        #   srun pipeline.sh ...

srun hostname
srun sleep 60
        sbatch_instructions = ["dsub", "", "", "", ""]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for launch script.')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Turns on verbosity.")
    parser.add_argument('--quick', '-q', dest='quick', action='store_true', help='Instead of re-generating the pairing index, reads from matches.csv (if exists).')
    parser.add_argument('--matches_log', '-l', dest='log', action='store_true', help='Instead of storing matches as CSV, stores them as LOG file with more detailed output.')

    parser.add_argument('--port', '-p', dest='port', default="50051", help='Selects the port for the server to run on.  Defaults to 50051 if not provided.')
    parser.add_argument('--latitude', '-lat', dest='latitude', default="38.7509000", help='This is the latitude the drone should be created at, if using a SITL simulation.  By default this will be in Manassas Va')
    parser.add_argument('--longitude', '-lon', dest='longitude', default="-77.4753000", help='This is the longitude the drone should be created at, if using a SITL simulation.  By default this will be in Manassas Va')

    args = parser.parse_args()

    if args.quick:
        callers = []
        csv_file = open('matches.csv', 'r')
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
        generate_sbatch_scripts(callers)
    else:
        callers = main()
        f = open('matches.csv', 'w')
        if args.log:
            for caller in callers:
                caller.dump_caller_info(f)
        else:
            for caller in callers:
                caller.dump_caller_info_csv(f)
        f.close()
        generate_sbatch_scripts(callers)
=======
def varscan_pipeline(caller):
    # Generate slurm job srun command
    job = "srun  "
    caller.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for the launch script.')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Turns on verbosity.")
    parser.add_argument('--match', '-m', dest='match', action='store_true',
                        help='Turns on the matching algorithm using the base file')
    parser.add_argument('--match_output_file', '-o', dest='match_output_file', default="matches.csv",
                        help='Determines the file to write matches out to (csv format).  Only needed with the --match flag.  Default is matches.csv.')



    # parser.add_argument('--port', '-p', dest='port', default="50051",
    #                     help='Selects the port for the server to run on.  Defaults to 50051 if not provided.')
    # parser.add_argument('--latitude', '-lat', dest='latitude', default="38.7509000",
    #                     help='This is the latitude the drone should be created at, if using a SITL simulation.  By default this will be in Manassas Va')
    # parser.add_argument('--longitude', '-lon', dest='longitude', default="-77.4753000",
    #                     help='This is the longitude the drone should be created at, if using a SITL simulation.  By default this will be in Manassas Va')

    args = parser.parse_args()
    callers = extract_matches()

    if args.match:
        f = open(args.match_output_file, 'w')
        for caller in callers:
            caller.dump_caller_info_csv(f)
        f.close()

    # Each match needs to be run through the pipeline
    for caller in callers:
        varscan_pipeline(caller)
>>>>>>> Stashed changes


