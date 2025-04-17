#!/bin/bash
#SBATCH -A birthright
#SBATCH -p high_mem_cd
#SBATCH --qos=birthright-high_mem_cd
#SBATCH -t 1-00:00:00
#SBATCH --nodes=1
#SBATCH -c 20
#SBATCH --mem=50g
#SBATCH -J eggnog
#SBATCH --output=eggnog_out_%j.log
#SBATCH --error=eggnog_err_%j.log

cache_dir=CACHE
options_file=TOML

fastas=$(ls *{.faa,.fasta})
for fasta in $fastas;
do
    apptainer exec --bind $cache_dir:/cache/  $cache_dir/stavisvols-eggnog_for_pd-latest.img eggnog_wrapper.py --task search --options $options_file --run_args "-i ${fasta} -o ${fasta} --output_dir ./ --data_dir ${cache_dir}/eggnog_db"
done

apptainer exec $cache_dir/stavisvols-eggnog_for_pd-latest.img quantify_annotations.py --options $options_file --gofile $cache_dir/gomap.tsv --namefile $cache_dir/annotation_names.tsv

