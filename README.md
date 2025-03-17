# PD_eggnog_quantification
This is a tool for 1: running eggnog annotations on fasta files and 2: using proteome discoverer peptide quantification data to quantify the fraction of observed peptide intensity associated with these functions. 
This tool is intended for use by the Hettich lab at ORNL and so it makes several assumptions about the available compute resources that will not be true for anyone else. 

## To install:
1. Log into CADES. The URL is or-slurm-login.ornl.gov. Use your 3 letter ID and password to log in. This is an SSH connection so either use MobaXterm or run `ssh <3letterID>@or-slurm-login.ornl.gov` on a bash terminal. 
2. Run `git clone https://github.com/stavis1/PD_eggnog_quantification` to download the code.
3. Run `cd PD_eggnog_quantification` to navigate to the code directory. 
4. Run `./install.sh` to set up the scripts for your account and download the eggnog database. 
5. Downloading the database takes several hours and you will have to wait until it finishes to use the tool. To check if the download job is still running run `squeue | grep $USER` to get a list of your running SLURM jobs and check for `DL_DB` in that list. 

## To run:
1. Collect the fasta/faa and PeptideGroups files into a single directory on CADES.
2. Run `sbatch ~/PD_eggnog_quantification/run.sbatch /path/to/your/data` the path to your data can be either relative or absolute. 
