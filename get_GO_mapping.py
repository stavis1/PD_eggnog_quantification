#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:16:30 2025

@author: 4vt
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', required=True, action = 'store',
                    help='The go.obo file.')
parser.add_argument('-o', '--output', required=True, action = 'store',
                    help='The mapping file to write.')
args = parser.parse_args()
import re

#define the GO term object class
class Term:
    def __init__(self, entry):
        self.id = re.search(r'id: (GO:\d{7})', entry).group(1)
        self.all_ids = set([self.id] + re.findall(r'alt_id: (GO:\d{7})', entry))
        self.ancestors = set(re.findall(r'(?:(?:is_a)|(?:replaced_by)): (GO:\d{7})', entry))
        self.parsed = not bool(len(self.ancestors))
        self.ancestors |= self.all_ids
    
    def get_ancestors(self, term_map):
        if self.parsed:
            return self.ancestors
        else:
            self.parsed = True
            new_ancestors = []
            for ancestor in self.ancestors:
                if not ancestor in self.all_ids:
                    new_ancestors.extend(term_map[ancestor].get_ancestors(term_map))
            self.ancestors.update(new_ancestors)
            return self.ancestors

    def report(self):
        ancestors = ';'.join(self.ancestors)
        report_str = '\n'.join(f'{i}\t{ancestors}' for i in self.all_ids)
        return report_str

#read in the relavent parts of the GO ontology file and split it into a list of term definitions
with open(args.input, 'r') as obo:
    entries = obo.read().split('[Typedef]')[0].split('[Term]')[1:]

#make GO term objects
terms = [Term(e) for e in entries]
term_map = {t.id:t for t in terms}

#get all terms implied by is_a relationships for each term
for term in terms:
    term.get_ancestors(term_map)

#write term mapping file
with open(args.output, 'w') as tsv:
    tsv.write('term\tancestors\n')
    tsv.write('\n'.join(t.report() for t in terms))

