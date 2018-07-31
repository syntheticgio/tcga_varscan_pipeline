import os
import os.path
import commands

class slurm_submitter():
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

    def __init__(self, base_dir):
        self.base_directory = base_dir
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
#SBATCH --dependency=afterok:{job_ids}
#SBATCH --chdir={working_directory}

cd {working_directory}

./pipeline.sh {normal_file_REF} {tumor_file_REF} {output_location} {barcode} {working_directory}/../references/{reference} {db_address}
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
#SBATCH --mem=1024
#SBATCH --chdir=/home/torcivia/tcga/

echo "Attempting to make directory..."
mkdir -p {working_directory}

echo "Moving to directory..."
cd {working_directory}

echo "Copying BAM files and indexes..."
gsutil cp {normal} ./ 2> download_normal.sterr
gsutil cp {tumor} ./ 2> download_tumor.stderr
gsutil cp {normal}.bai ./ 2> download_normal_bai.stderr
gsutil cp {tumor}.bai ./ 2> download_tumor_bai.stderr

echo "Copying script files ..."
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/pipeline.sh ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/post_json.py ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/split_by_ref.sh ./
cp /home/torcivia/pipeline/tcga_varscan_pipeline/src/transfer_clean.sh ./

echo "Changing permissions..."
chmod +x split_by_ref.sh
chmod +x pipeline.sh
chmod +x transfer_clean.sh

echo "Splitting by reference..."
./split_by_ref.sh {normal} {tumor} {db_address}
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

rm -rf {working_directory}
        
        """

    def populate_template(self, caller, node, job_type, reference="download", job_ids=0):
        barcode = caller.barcode
        normal = caller.normal_file_url
        tumor = caller.tumor_file_url
        normal_file = caller.normal_file
        tumor_file = caller.tumor_file
        
        self.tcga_barcode = caller.barcode # set here for other purposes (launching)
        db_address = "35.231.62.194"
        # Construct output location
        output_location = "gs://iron-eye-6998/tcga_wgs_results/" + barcode + "/"
        self.slurm_file = barcode + "_" + job_type + "_" + reference + ".slurm"
        working_directory = self.base_directory + caller.barcode + "/"
        

        if job_type == "DOWNLOAD":
            self.template = self.download_template.format(**vars())
        elif job_type == "VARCALL":
            normal_file_REF = normal_file.rsplit(".", 1)[0] + ".REF_" + reference.rsplit(".", 1)[0] + ".bam"
            tumor_file_REF = tumor_file.rsplit(".", 1)[0] + ".REF_" + reference.rsplit(".", 1)[0] + ".bam"
            self.template = self.varcall_template.format(**vars())
            # print self.template
        elif job_type == "CLEAN":
            self.job_type = job_type
            self.job_ids = job_ids
            self.template = self.clean_template.format(**vars())
            # print self.template
        else:
            print ("ERROR: Couldn't find job_type template.")

    def launch_job(self):
        jobdir = os.path.join(self.base_directory, self.tcga_barcode)
        jobdir = os.path.abspath(jobdir)
        if not os.path.exists(jobdir):
            try:
                os.makedirs(jobdir)
            except:
                print "Error creating directory!"

        # Construct directory.

        filename = os.path.join(jobdir, self.slurm_file)
        print("Filename: {}".format(filename))
        outfile = open(filename, 'w')
        outfile.write(self.template)
        outfile.close()

        print "OUTDIR: %s" % jobdir
        # print "SLURM FILE: %s" % filename
        if self.job_type == "CLEAN":
            _ids = ','.join('afterok:{}'.format(str(c)) for c in self.job_ids)
            output = commands.getoutput('sbatch --dependency={} {}'.format(_ids, filename))
            #print("IDS: {}".format(_ids))
            #print("filename: {}".format(filename))
            print ('sbatch --dependency={} {}'.format(_ids, filename))
            #pass
        elif self.job_type == "DOWNLOAD":
            output = commands.getoutput('sbatch --dependency=afterok:{} {}'.format(self.download_id, filename))
            self.download_id=output.split()[3]
            print('sbatch --dependency=afterok:{} {}'.format(self.download_id, filename))
            #print("output: {}".format(output))
        else:
            output = commands.getoutput('sbatch {}'.format(filename))
            print('sbatch {}'.format(filename))

        #output = 555  # temporary
        return output.split()[3]

        
