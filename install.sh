#!/bin/bash

#pull the singularity container for eggnog
cache_dir=$(find ./ -name cache -type d | xargs realpath)
if [ ! -f $cache_dir/stavisvols-eggnog_for_pd-latest.img ]; then
    module load PE-gnu
    module load singularity
    singularity build --force $cache_dir/stavisvols-eggnog_for_pd-latest.img docker://stavisvols/eggnog_for_pd:latest
fi

#parse the GO ontology definiton file
if [ ! -f $cache_dir/gomap.tsv ]; then
    wget https://current.geneontology.org/ontology/go.obo -P $cache_dir
    module load python
    goparser=$(find ./ -name get_GO_mapping.py)
    python $goparser --input $cache_dir/go.obo --output $cache_dir/gomap.tsv
fi

#download annotation term descriptions
if [ ! -f $cache_dir/annotation_names.tsv ]; then
    wget https://figshare.com/ndownloader/files/53085347 -O $cache_dir/annotation_names.tsv
fi

#if the user has access to BSD resources use those instead of birthright
run_script=$(find ./ -name run.sbatch)
db_script=$(find ./ -name download_DB.sbatch)
if sacctmgr show User $USER --associations | grep -q 'bsd-batch'; then
    sed -i 's/birthright/bsd/g' $run_script
    sed -i 's/high_mem_cd/batch/g' $run_script
    sed -i 's/birthright/bsd/g' $db_script
    sed -i 's/high_mem_cd/batch/g' $db_script
fi

#add the cache dir and options file to the slurm scripts
toml=$(find ./ -name options.toml | xargs realpath)
sed -i "s@CACHE@${cache_dir}@g" $run_script
sed -i "s@CACHE@${cache_dir}@g" $db_script
sed -i "s@TOML@${toml}@g" $run_script
sed -i "s@TOML@${toml}@g" $db_script

#download eggnog database
if [ ! -d $cache_dir/eggnog_db ]; then
    sbatch $db_script
    echo 'Please wait for the eggnog database to be downloaded; this will take several hours.'
    echo 'To check if the job is still running execute "squeue | grep $USER" and look for "DL_DB".'
fi

