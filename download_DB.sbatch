#!/bin/bash
#SBATCH -A birthright
#SBATCH -p high_mem_cd
#SBATCH --qos=birthright-high_mem_cd
#SBATCH -t 1-00:00:00
#SBATCH --nodes=1
#SBATCH -c 1
#SBATCH --mem=32g
#SBATCH -J DL_DB
#SBATCH --output=DL_DB_out_%j.log
#SBATCH --error=DL_DB_err_%j.log

cache_dir=CACHE
options_file=TOML

module load singularity
mkdir $cache_dir/eggnog_db
singularity exec --no-home --bind $cache_dir:/cache/  $cache_dir/stavisvols-eggnog_for_pd-latest.img eggnog_wrapper.py --task download --options $options_file --run_args "-y --data_dir ${cache_dir}/eggnog_db"





