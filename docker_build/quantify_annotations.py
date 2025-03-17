#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 11:29:52 2025

@author: 4vt
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--options', action = 'store', required = True,
                    help = 'The TOML formatted options file')
args = parser.parse_args()

import os
import tomli
import numpy as np
import pandas as pd
from copy import copy
from collections import defaultdict

with open(args.options, 'rb') as toml:
    options = tomli.load(toml)['rollup_params']

#set up data objects
class keydefaultdict(defaultdict):
    '''
    subclass of defaultdict that passes the key to the first
    argument of the default function
    '''
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class Peptide:
    def __init__(self, sequence, proteins, intensities):
        self.sequence = sequence
        self.proteins = proteins.split(';')
        self.intensities = np.array(intensities, dtype = np.float64)
        self.coherent_terms = set()
        self.all_terms = set()
    
    def annotate(self, annotations):
        term_sets = [annotations[p] for p in self.proteins]
        coherent_terms = term_sets.pop()
        all_terms = copy(coherent_terms)
        
        for term_set in term_sets:
            coherent_terms &= term_set
            all_terms |= term_set
        self.coherent_terms = coherent_terms
        self.all_terms = all_terms
        
class Term:
    def __init__(self, annotation_type, term):
        self.annotation_type = annotation_type
        self.term = term
        self.id = (annotation_type, term)
        self.coherent_intensity = np.full(sample_sums.shape, np.nan)
        self.N_coherent = np.full(sample_sums.shape, 0)
        self.all_intensity = np.full(sample_sums.shape, np.nan)
        self.N_all = np.full(sample_sums.shape, 0)
        self.contributing_proteins = set()
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, o):
        return hash(self) == hash(0)
    
    def add_peptide(self, peptide):
        self.all_intensity = np.nansum((self.all_intensity, peptide.intensities), axis = 0)
        self.N_all += np.isfinite(peptide.intensities)
        self.contributing_proteins.update(peptide.proteins)
        if self.id in peptide.coherent_terms:
            self.coherent_intensity = np.nansum((self.coherent_intensity, peptide.intensities), axis = 0)
            self.N_coherent += np.isfinite(peptide.intensities)
    
    def report(self):
        self.coherent_intensity = self.coherent_intensity/sample_sums
        self.all_intensity = self.all_intensity/sample_sums
        report_data = {'annotation_type':self.annotation_type,
                       'term':self.term,
                       'contributing_proteins':';'.join(self.contributing_proteins)}
        report_data.update({f'coherent_intensity_{c[11:]}':i for c, i in zip(quantcols, self.coherent_intensity)})
        report_data.update({f'N_coherent_peptides_{c[11:]}':i for c, i in zip(quantcols, self.N_coherent)})
        report_data.update({f'all_intensity_{c[11:]}':i for c, i in zip(quantcols, self.all_intensity)})
        report_data.update({f'N_all_peptides_{c[11:]}':i for c, i in zip(quantcols, self.N_all)})
        return pd.Series(report_data)


#read in peptide quant data
pepfiles = [f for f in os.listdir() if f.endswith('PeptideGroups.txt')]
pepdata = []
for pepfile in pepfiles:
    data = pd.read_csv(pepfile, sep = '\t')
    data.index = [f'{s} {m}' if type(m) == str else s for s, m in zip(data['Sequence'], data['Modifications'])]
    quantcols = [c for c in data.columns if c.startswith('Abundance: ')]
    data = data[['Protein Accessions'] + quantcols]
    data.columns = [f'proteins {pepfile}'] + list(data.columns)[1:]
    pepdata.append(data)
pepdata = pd.concat(pepdata, axis = 1)
protrows = zip(*[pepdata[c] for c in pepdata.columns if c.startswith('proteins ')])
pepdata['proteins'] = [';'.join(set(p for prs in row if type(prs) == str for p in prs.split('; '))) for row in protrows]
quantcols = [c for c in pepdata.columns if c.startswith('Abundance: ')]
peptides = [Peptide(s, p, i) for s, p, i in zip(pepdata.index, pepdata['proteins'], zip(*[pepdata[c] for c in quantcols]))]
sample_sums = np.nansum(pepdata[quantcols].to_numpy(), axis = 0)

#read protein annotation data
annotation_files = [f for f in os.listdir() if f.endswith('.emapper.annotations')]
annotations = defaultdict(lambda:set())
for annotation_file in annotation_files:
    data = pd.read_csv(annotation_file, sep = '\t', skiprows = 4)
    data = data[[c for c in data.columns if not c in options['exclude_columns']]]
    data = data.replace('-', 'unannotated')
    data = data.replace(np.nan, 'unannotated')
    annotation_types = list(data.columns)[1:]
    for protein, term_sets in zip(data['#query'], zip(*[data[c] for c in annotation_types])):
        for ann_type, term_set in zip(annotation_types, term_sets):
            if ann_type == 'COG_category':
                terms = term_set.split()
            else:
                terms = term_set.split(',')
            for term in terms:
                annotations[protein].add((ann_type, term))

#add annotations to peptides
for peptide in peptides:
    peptide.annotate(annotations)

#gather annotation data
terms = keydefaultdict(lambda x: Term(*x))
for peptide in peptides:
    for term in peptide.all_terms:
        terms[term].add_peptide(peptide)

#write results
results = pd.DataFrame([t.report() for t in terms.values()])
results = results.sort_values(['annotation_type', 'term'])
results.to_csv('quantified_eggnog_annotations.tsv', sep = '\t', index = False)
