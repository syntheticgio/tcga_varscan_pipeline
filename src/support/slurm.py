import os
import os.path
# import commands
import subprocess
from time import time
import pyslurm
from time import gmtime, strftime


class slurm_submitter:
    # TODO This needs to be updated to not specifically use my directory structure
    template = ""
    varcall_template = ""
    download_template = ""
    tcga_barcode = ""
    job_type = ""
    reference = ""
    node = ""
    working_directory = ""
    normal = ""
    tumor = ""
    slurm_file = ""
    job_ids = []
    base_directory = ""
    download_id = 0
    indx = 0

    sample_id_lists = {}
    sample_by_id_lookup = {}

    def __init__(self, base_dir, output_bucket=None):
        self.base_directory = base_dir
        self.output_bucket = output_bucket
        self.test_template = """\
#!/bin/bash

#SBATCH --job-name=test-job 
#SBATCH --output=test_%A_job.stout
#SBATCH --error=test_%A_job.sterr

#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=torcivia@gwu.edu

#SBATCH --nodelist={node}

#SBATCH --ntasks=1
#SBATCH --mem=1024
#SBATCH --chdir={working_directory}
#SBATCH --comment="TEST"

echo "Moving to directory..."
cd {working_directory}

echo "Copying script file ..."
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/test.py ./

echo "Generating the 37th entry of the Fibonacci sequence"
python3 test.py
echo "test.py : "$? 
        """

        self.varcall_template = """\
#!/bin/bash

#SBATCH --job-name={barcode}_{reference}_{job_type} 
#SBATCH --output={barcode}_%A_{reference}.stout
#SBATCH --error={barcode}_%A_{reference}.sterr

#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=torcivia@gwu.edu

#SBATCH --nodelist={node}

#SBATCH --ntasks=1
#SBATCH --mem=6400
#SBATCH --dependency=afterany:{job_ids}
#SBATCH --chdir={working_directory}
#SBATCH --comment={job_type}

cd {working_directory}

./pipeline.sh {normal_file_REF} {tumor_file_REF} {output_location} {barcode} {working_directory}/../references/{reference} {db_address}
echo "pipeline.sh : "$? 
        """

        self.download_template = """\
#!/bin/bash

#SBATCH --job-name={barcode}_{reference}_{job_type} 
#SBATCH --output={barcode}_%A_{reference}.stout
#SBATCH --error={barcode}_%A_{reference}.sterr

#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=torcivia@gwu.edu

#SBATCH --nodelist={node}

#SBATCH --ntasks=1
#SBATCH --comment={job_type}
#SBATCH --mem=25600

#SBATCH --chdir=/home/torcivia/tcga/
{dependency_sbatch}

echo "Attempting to make directory..."
mkdir -p {working_directory}

echo "Moving to directory..."
cd {working_directory}

# echo "Attempting to make bucket directory and link it..."
# mkdir -p {working_directory}/tcga_bucket/
# gcsfuse --implicit-dirs gdc-tcga-phs000178-controlled {working_directory}/tcga_bucket/

echo "Copying script files ..."
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/pipeline.sh {working_directory}
echo "cp pipeline.sh ./ : "$?
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/post_json.py {working_directory}
echo "cp post_json.py ./ : "$?
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/split_by_ref.sh {working_directory}
echo "cp split_by_ref.sh ./ : "$?
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/transfer_clean.sh {working_directory}
echo "cp transfer_clean.sh ./ : "$?
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/re_chrom_name.awk {working_directory}
echo "cp re_chrom_name.awk ./ : "$?

echo "Changing permissions..."
chmod +x split_by_ref.sh
chmod +x pipeline.sh
chmod +x transfer_clean.sh

echo "Copying BAM files and indexes..."
gsutil cp {normal} ./ 2> download_normal.sterr
# ln -s {normal} ./
echo "gsutil {normal} ./ : "$? 

gsutil cp {tumor} ./ 2> download_tumor.stderr
# ln -s {tumor} ./
echo "gsutil {tumor} ./ : "$?

touch *.bam

gsutil cp {normal}.bai ./ 2> download_normal_bai.stderr
# ln -s {normal}.bai ./
echo "gsutil {normal}.bai ./ : "$?

gsutil cp {tumor}.bai ./ 2> download_tumor_bai.stderr
# ln -s {tumor}.bai ./
echo "gsutil {tumor}.bai ./ : "$? 

touch *.bai

echo "Splitting by reference..."
./split_by_ref.sh {normal} {tumor} {db_address}
echo "split_by_ref.sh : "$? 
        """

        self.clean_template = """\
#!/bin/bash

#SBATCH --job-name={barcode}_{reference}_{job_type} 
#SBATCH --output={barcode}_%A_{reference}.stout
#SBATCH --error={barcode}_%A_{reference}.sterr

#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=torcivia@gwu.edu

#SBATCH --nodelist={node}

#SBATCH --ntasks=1
#SBATCH --mem=1024
#SBATCH --chdir={working_directory}
#SBATCH --comment={job_type}

./transfer_clean.sh {normal_file} {tumor_file} {output_location} {barcode} {working_directory}/../references/{reference} {db_address}
echo "transfer_clean.sh : "$? 

# rm -rf {working_directory}
        
        """

    def populate_template(self, caller, node, job_type, db_address, reference="download", job_ids=0):
        # Capture test first to avoid having to deal with caller etc.
        self.job_type = job_type
        if job_type == "TEST":
            # Just put the test output in the working directory
            working_directory = self.base_directory
            self.template = self.test_template.format(**vars())
            self.slurm_file = "test_run_{}.slurm".format(time())
            return

        if self.output_bucket is None:
            print(" ERROR!  Output Bucket is not set.  Please set in config file.  Aborting!")
            exit(1)

        # While some of these variables appear to not be used; they are being used in the **vars() calls below silently.
        barcode = caller.barcode
        working_directory = self.base_directory + barcode + "/"
        # For gcsfuse - DOES NOT WORK FOR THESE PURPOSES!
        # normal = caller.normal_file_url.replace("gs://gdc-tcga-phs000178-controlled/", "{}tcga_bucket/".format(working_directory))
        # tumor = caller.tumor_file_url.replace("gs://gdc-tcga-phs000178-controlled/", "{}tcga_bucket/".format(working_directory))
        normal = caller.normal_file_url
        tumor = caller.tumor_file_url
        normal_file = caller.normal_file
        tumor_file = caller.tumor_file

        self.tcga_barcode = caller.barcode  # set here for other purposes (launching)
        # db_address = "35.231.62.194"
        # Construct output location
        output_location = self.output_bucket + barcode + "/"
        self.slurm_file = barcode + "_" + job_type + "_" + reference + ".slurm"

        if job_type == "DOWNLOAD":
            # This is used in the **vars() call.
            if job_ids != -1:
                dependency_sbatch = "#SBATCH --dependency=afterany:{}".format(job_ids)
            else:
                dependency_sbatch = ""
            self.template = self.download_template.format(**vars())
        elif job_type == "VARCALL":
            # These are used in the **vars() call.
            normal_file_REF = normal_file.rsplit(".", 1)[0] + ".REF_" + reference.rsplit(".", 1)[0] + ".bam"
            tumor_file_REF = tumor_file.rsplit(".", 1)[0] + ".REF_" + reference.rsplit(".", 1)[0] + ".bam"
            self.template = self.varcall_template.format(**vars())
        elif job_type == "CLEAN":
            self.job_ids = job_ids
            self.template = self.clean_template.format(**vars())
        else:
            print("ERROR: Couldn't find job_type template.")

    def launch_job(self):
        jobdir = os.path.join(self.base_directory, self.tcga_barcode)
        jobdir = os.path.abspath(jobdir)
        if not os.path.exists(jobdir):
            try:
                os.makedirs(jobdir)
            except BaseException as e:
                print("Error creating directory! %s", e)

        # Construct directory.

        filename = os.path.join(jobdir, self.slurm_file)
        print("Writing template to {} for job launching.".format(filename))
        # Write out template here
        with open(filename, 'w') as batch_file:
            batch_file.write(self.template)

        # Catch any special types of job types that need to be run here.
        # Otherwise the else clause is the one that should run everything if possible.

        if self.job_type == "CLEAN":
            _ids = ','.join('afterany:{}'.format(str(c)) for c in self.job_ids)
            cmd = ["sbatch", "--dependency={}".format(_ids), filename]
            output = subprocess.check_output(cmd)
            print('sbatch --dependency={} {}'.format(_ids, filename))
        else:
            output = subprocess.check_output(['sbatch', filename])
            print('sbatch {}'.format(filename))

        return_ids = output.split()[3].decode('UTF-8')
        # Record a list of job ids by TCGA Barcode (might come in handy!)
        if self.tcga_barcode not in self.sample_id_lists:
            self.sample_id_lists[self.tcga_barcode] = {}
        if self.job_type not in self.sample_id_lists[self.tcga_barcode]:
            self.sample_id_lists[self.tcga_barcode][self.job_type] = []
        self.sample_id_lists[self.tcga_barcode][self.job_type].append(int(return_ids))
        # Create lookup table for all job_ids w/ tcga barcode as their entry
        self.sample_by_id_lookup[int(return_ids)] = self.tcga_barcode
        if self.job_type == "CLEAN":
            print("DEBUG: {}".format(self.sample_id_lists[self.tcga_barcode]))
        return return_ids

    def query_all_jobs(self):
        jobs = pyslurm.job().get()

        if jobs:
            job_info = {}
            date_fields = ['start_time', 'suspend_time', 'submit_time', 'end_time', 'eligible_time', 'resize_time']
            other_fields = ['run_time', 'run_time_str', 'nodes', 'job_state', 'command', 'comment']

            for key, value in jobs.items():
                try:
                    tcga_barcode = self.sample_by_id_lookup[key]
                except KeyError:
                    # print("Looks like there is a job that is running which isn't tracked in our internal database.")
                    # Skip
                    continue
                if tcga_barcode not in job_info:
                    job_info[tcga_barcode] = {key: {}}
                else:
                    job_info[tcga_barcode][key] = {}

                for part_key in sorted(value.keys()):
                    if part_key in date_fields:
                        if value[part_key] == 0:
                            job_info[tcga_barcode][key][part_key] = "NA"
                        else:
                            ddate = gmtime(value[part_key])
                            ddate = strftime("%a %b %d %H:%M:%S %Y", ddate)
                            job_info[tcga_barcode][key][part_key] = ddate
                    elif part_key in other_fields:
                        job_info[tcga_barcode][key][part_key] = value[part_key]
            return job_info
        return None

    # TODO: Not sure if this is needed or not...placeholder
    def query_by_barcode(self, barcode):
        job_id_dict = self.sample_id_lists[barcode]

    def query_node_status(self, nodes=None):
        # nodes is a list of requested nodes to send back
        node_dict = pyslurm.node().get()
        node_list = {}
        if len(node_dict) > 0:
            # CPU_LOAD = Load AVG
            # FREE_MEM = Free memory in Megabytes
            fetch_list = ['state', 'free_mem', 'cpu_load', 'cores', 'real_memory']
            for key, value in node_dict.items():
                # key = slurm-child3, for example
                # value is a bunch of other info:

                # TODO: Check to make sure this works ... think key in nodes could be an error?
                if nodes is None or key in nodes:
                    node_list[key] = {}
                    for part_key in sorted(value.keys()):
                        if part_key in fetch_list:
                            node_list[key][part_key] = value[part_key]
        return node_list
