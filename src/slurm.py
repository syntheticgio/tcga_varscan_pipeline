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

setenv WORKDIR {working_directory}
mkdir -p $WORKDIR
cd $WORKDIR

srun pipeline.sh {normal_file} {tumor_file} {output_location} {barcode} {working_directory}/../references/{reference} {db_address}
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
#SBATCH --chdir={working_directory}

setenv WORKDIR {working_directory}
mkdir -p $WORKDIR
cd $WORKDIR

gsutil cp {normal} ./
gsutil cp {tumor} ./
gsutil cp {normal}.bai ./
gsutil cp {tumor}.bai ./

cp /home/torcivia/tcga_varscan_pipeline/src/pipeline.sh ./        
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
            #print ('sbatch --dependency={} {}'.format(_ids, filename))
        else:
            output = commands.getoutput('sbatch {}'.format(filename))
            #print('sbatch {}'.format(filename))
        # Submit to PBS
        # output = commands.getoutput('sbatch %(filename)s' % vars())
        # print outputt

        #output = 555  # temporary
        return output

        
