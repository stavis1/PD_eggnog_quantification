#!/bin/bash
#SBATCH -A birthright
#SBATCH -p high_mem_cd
#SBATCH --qos=birthright-high_mem_cd
#SBATCH -t 1-00:00:00
#SBATCH --nodes=1
#SBATCH -c 4
#SBATCH --mem=50g
#SBATCH -J eggnog
#SBATCH --output=eggnog_out_%j.log
#SBATCH --error=eggnog_err_%j.log

cache_dir=CACHE
options_file=TOML


