import os
import os.path
# import commands
import subprocess
from time import time


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

    def __init__(self, base_dir):
        self.base_directory = base_dir
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
#SBATCH --mem=1024
#SBATCH --dependency=afterany:{job_ids}
#SBATCH --chdir={working_directory}

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
#SBATCH --chdir=/home/torcivia/tcga/
{download_job_id}

echo "Attempting to make directory..."
mkdir -p {working_directory}

echo "Moving to directory..."
cd {working_directory}

echo "Copying BAM files and indexes..."
gsutil cp {normal} ./ 2> download_normal.sterr
echo "GSUTIL {normal} : "$? 
gsutil cp {tumor} ./ 2> download_tumor.stderr
echo "GSUTIL {tumor} : "$?

gsutil cp {normal}.bai ./ 2> download_normal_bai.stderr
echo "GSUTIL {normal}.bai : "$?
gsutil cp {tumor}.bai ./ 2> download_tumor_bai.stderr
echo "GSUTIL {tumor}.bai : "$? 

sleep 2

touch {normal}.bai
touch {tumor}.bai

echo "Copying script files ..."
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/pipeline.sh ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/post_json.py ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/split_by_ref.sh ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/transfer_clean.sh ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/re_chrom_name.awk ./

echo "Changing permissions..."
chmod +x split_by_ref.sh
chmod +x pipeline.sh
chmod +x transfer_clean.sh

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

./transfer_clean.sh {normal_file} {tumor_file} {output_location} {barcode} {working_directory}/../references/{reference} {db_address}
echo "transfer_clean.sh : "$? 

rm -rf {working_directory}
        
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

        # While some of these variables appear to not be used; they are being used in the **vars() calls below silently.
        barcode = caller.barcode
        normal = caller.normal_file_url
        tumor = caller.tumor_file_url
        normal_file = caller.normal_file
        tumor_file = caller.tumor_file

        self.tcga_barcode = caller.barcode  # set here for other purposes (launching)
        # db_address = "35.231.62.194"
        # Construct output location
        output_location = "gs://iron-eye-6998/tcga_wgs_results/" + barcode + "/"
        self.slurm_file = barcode + "_" + job_type + "_" + reference + ".slurm"
        working_directory = self.base_directory + caller.barcode + "/"

        if job_type == "DOWNLOAD":
            # This is used in the **vars() call.
            if job_ids != -1:
                download_job_id = "#SBATCH --dependency=afterany:{}".format(job_ids)
            else:
                download_job_id = ""
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
            # output = subprocess.check_output(cmd)
            print('sbatch --dependency={} {}'.format(_ids, filename))
            return "7000000"
            # pass
        # elif self.job_type == "DOWNLOAD":
        #     output = subprocess.check_output('sbatch --dependency=afterok:{} {}'.format(self.download_id, filename))
        #     # self.download_id = output.split()[3]
        #     print('sbatch --dependency=afterok:{} {}'.format(self.download_id, filename))
        #     # print("output: {}".format(output))
        else:
            output = subprocess.check_output(['sbatch', filename])
            print('sbatch {}'.format(filename))

        # output = 555  # temporary
        print("OUTPUT: {}".format(output))
        return output.split()[3].decode('UTF-8')
