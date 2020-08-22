#!/usr/bin/python

#This script prints out the TCGA barcode along with the cancer type
# in csv format
import csv
new_dict = {}
barcode_list = []
cancer_list = {"BLCA":0,"BRCA":0,"CESC":0,"COAD":0,"DLBC":0,"ESCA":0,"GBM":0,"HNSC":0,"KICH":0,"KIRC":0,"KIRP":0,"LAML":0,"LGG":0,"LIHC":0,"LUAD":0,"LUSC":0,"OV":0,"PRAD":0,"READ":0,"SARC":0,"SKCM":0,"STAD":0,"THCA":0,"UCEC":0,"UVM":0, "disease_code":0}

with open('barcode_cancer.csv', 'rb') as cancerfile:
    barcodereader = csv.reader(cancerfile, delimiter=',')
    for brow in barcodereader:
        new_dict[brow[0]] = brow[1]
        

with open('matches_normal_sorted.csv', 'rb') as csvfile:
    tcga_reader = csv.reader(csvfile, delimiter=',')
    for row in tcga_reader:
        # the TCGA ID (most of it): GS bucket location
        #barcode_list.append(row[1])
        print("{},{}".format(row[1], new_dict[row[1]]))
        #new_dict.append(tcga_dict)

# with open('barcode_cancer_unique.csv', 'rb') as csvfile2:
#     tcga_reader2 = csv.reader(csvfile2, delimiter=',')
#     for row2 in tcga_reader2:
#         cancer_list[row2[1]] += 1


# print(cancer_list) 
