import os
import os.path
import commands

class slurm_submitter():
    template = ""
    varcall_template = ""
    download_template = ""
    barcode = ""
    job_type = ""
    reference = ""
    node = ""
    working_directory = ""
    normal = ""
    tumor = ""

    def __init__(self):
        self.varcall_template = """\
        #!/bin/bash
        
        #SBATCH --job-name=%(barcode)s_%(reference)s_%(job_type)s 
        #SBATCH --output=%(barcode)s_%A_%(reference)s.stout
        #SBATCH --error=%(barcode)s_%A_%(reference)s.sterr
        
        #SBATCH --mail-type=FAIL,END
        #SBATCH --mail-user=torcivia@gwu.edu
        
        #SBATCH --nodelist=%(node)s
        
        #SBATCH --ntasks=1
        #SBATCH --mem=1024
        #SBATCH --dependency=afterok:%(job_ids)s
        #SBATCH --chdir=%(working_directory)s
        
        setenv WORKDIR %(working_directory)s
        mkdir -p ${WORKDIR}
        cd ${WORKDIR}

        srun pipeline.sh ...
        """

        self.download_template = """\
        #!/bin/bash
        
        #SBATCH --job-name=%(barcode)s_%(reference)s_%(job_type)s 
        #SBATCH --output=%(barcode)s_%A_%(reference)s.stout
        #SBATCH --error=%(barcode)s_%A_%(reference)s.sterr
        
        #SBATCH --mail-type=FAIL,END
        #SBATCH --mail-user=torcivia@gwu.edu
        
        #SBATCH --nodelist=%(node)s
        
        #SBATCH --ntasks=1
        #SBATCH --mem=1024
        #SBATCH --chdir=%(working_directory)s
        
        setenv WORKDIR %(working_directory)s
        mkdir -p ${WORKDIR}
        cd ${WORKDIR}

        gsutil cp %(normal)s ./
        gsutil cp %(tumor)s ./
        gsutil cp %(normal)s.bai ./
        gsutil cp %(tumor)s.bai ./

        cp /home/torcivia/tcga_varscan_pipeline/src/pipeline.sh ./        
        """
    
        self.clean_template = """\
        #!/bin/bash
        
        #SBATCH --job-name=%(barcode)s_%(reference)s_%(job_type)s 
        #SBATCH --output=%(barcode)s_%A_%(reference)s.stout
        #SBATCH --error=%(barcode)s_%A_%(reference)s.sterr
        
        #SBATCH --mail-type=FAIL,END
        #SBATCH --mail-user=torcivia@gwu.edu
        
        #SBATCH --nodelist=%(node)s
        
        #SBATCH --ntasks=1
        #SBATCH --mem=1024
        #SBATCH --chdir=%(working_directory)s
        
        setenv WORKDIR %(working_directory)s
        mkdir -p ${WORKDIR}
        cd ${WORKDIR}

        gsutil cp %(normal)s ./
        gsutil cp %(tumor)s ./
        gsutil cp %(normal)s.bai ./
        gsutil cp %(tumor)s.bai ./
        
        """

    def populate_template(self, caller, node, job_type, working_directory, reference="None"):
        self.barcode = caller.barcode
        self.job_type = job_type
        self.reference = reference
        self.node = node
        self.working_directory = working_directory
        self.normal = caller.normal_file_url
        self.tumor = caller.tumor_file_url

        if job_type == "DOWNLOAD":
            self.template = self.download_template % vars()
            print self.template
        elif job_type == "VARCALL":
            self.template = self.varcall_template % vars()
        elif job_type == "CLEAN":
            self.template = self.clean_template % vars()
        else:
            print ("ERROR: Couldn't find job_type template.")

    def launch_job(self)
        
        jobname = molecule
        
        jobdir = os.path.join('systems', molecule)
        jobdir = os.path.abspath(jobdir)

        
        # Construct directory.
        filename = os.path.join(jobdir, 'run.slurm')
        outfile = open(filename, 'w')
        outfile.write(pbs)
        outfile.close()

        # Submit to PBS
        output = commands.getoutput('sbatch %(filename)s' % vars());
        print output

        
