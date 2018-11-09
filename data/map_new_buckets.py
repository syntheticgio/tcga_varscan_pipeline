#!/bin/python

import csv

new_dict = []

with open('TCGA_WGS_metadata_new_results.csv', 'rb') as csvfile:
    tcga_reader = csv.reader(csvfile, delimiter=',')
    i = 0
    for row in tcga_reader:
        if i == 0:
            HEADER = row
            i = i + 1
            continue
        # the TCGA ID (most of it): GS bucket location
        tcga_dict = {row[4]:row[15]}
        new_dict.append(tcga_dict)

with open('matches_normal_sorted.csv', 'rb') as csvfile2:
    csvfile_output = open('new_output.csv', 'w')
    tcga_writer = csv.writer(csvfile_output, delimiter=",")
    tcga_reader2 = csv.reader(csvfile2, delimiter=',')
    for row in tcga_reader2:
        b = row[2].split('-')
        bc = b[0] + '-' + b[1] + '-' + b[2] + '-' + b[3]
        b2 = row[8].split('-')
        bc2 = b2[0] + '-' + b2[1] + '-' + b2[2] + '-' + b2[3]
        nr1 = ""
        nr2 = ""
        for d in new_dict:
            if bc in d:
                nr1 = d[bc]
                break
        for d in new_dict:
            if bc2 in d:
                nr2 = d[bc2]
                break
        row.append(nr1)
        row.append(nr2)
        print row
        tcga_writer.writerow(row)
