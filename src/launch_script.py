import csv
from tcga import TCGAVariantCaller
import json
import os

def main():
    json_data=open('config.json').read()
    config = json.loads(json_data)

    VAR_INDEX = 0
    VAR_CALLERS = []
    HEADER = []
    MYDIR = os.path.dirname(__file__)
    MYFILE = os.path.join(MYDIR, config["input_file"])
    print(MYDIR)
    with open('full-results-normal.csv', 'rb') as csvfile:
        tcga_reader = csv.reader(csvfile, delimiter=',')
        i = 0
        # This assumes that there is a header in the csv file
        # and that the matches are rows that follow each other
        # TODO: Check to make sure header is proper (i.e. what is being expected)
        for row in tcga_reader:
            if i == 0:
                HEADER = row
                i = i + 1
                continue
            if i % 2 == 1:  # odd - first entry in group
                # create new var caller object
                var_caller = TCGAVariantCaller(VAR_INDEX)

                # Get barcode info
                print(row[3])
                barcode_info = row[3].split('-')

                barcode = barcode_info[0] + "-" + barcode_info[1] + "-" + barcode_info[2]
                var_caller.set_barcode(barcode)

                # Get the tumor / normal type
                if int(barcode_info[3][:2]) < 10:
                    # This is a tumor sample
                    var_caller.set_tumor_gdc_id(row[0])
                    var_caller.set_tumor_file(row[4])
                    var_caller.set_tumor_file_size(row[5])
                    var_caller.set_tumor_platform(row[6])
                    var_caller.set_tumor_file_url(row[7])
                    var_caller.set_tumor_barcode(row[3])
                else:
                    # This is a normal sample
                    var_caller.set_normal_gdc_id(row[0])
                    var_caller.set_normal_file(row[4])
                    var_caller.set_normal_file_size(row[5])
                    var_caller.set_normal_platform(row[6])
                    var_caller.set_normal_file_url(row[7])
                    var_caller.set_normal_barcode(row[3])

                # Get project info
                project_info = row[2].split('-')
                cancer_type = project_info[1]
                var_caller.set_cancer_type(cancer_type)

                VAR_CALLERS.append(var_caller)
            else:
                # Get barcode info
                barcode_info = row[3].split('-')
                
                if int(barcode_info[3][:2]) < 10:
                    # This is a tumor sample
                    VAR_CALLERS[VAR_INDEX].set_tumor_gdc_id(row[0])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file(row[4])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file_size(row[5])
                    VAR_CALLERS[VAR_INDEX].set_tumor_platform(row[6])
                    VAR_CALLERS[VAR_INDEX].set_tumor_file_url(row[7])
                    VAR_CALLERS[VAR_INDEX].set_tumor_barcode(row[3])
                else:
                    # This is a normal sample
                    VAR_CALLERS[VAR_INDEX].set_normal_gdc_id(row[0])
                    VAR_CALLERS[VAR_INDEX].set_normal_file(row[4])
                    VAR_CALLERS[VAR_INDEX].set_normal_file_size(row[5])
                    VAR_CALLERS[VAR_INDEX].set_normal_platform(row[6])
                    VAR_CALLERS[VAR_INDEX].set_normal_file_url(row[7])
                    VAR_CALLERS[VAR_INDEX].set_normal_barcode(row[3])

                #if config["debug"]:
                #    VAR_CALLERS[VAR_INDEX].dump_caller_info()

                # Compare barcodes
                tumor_barcode = barcode_info[0] + "-" + barcode_info[1] + "-" + barcode_info[2]
                normal_barcode_info = VAR_CALLERS[VAR_INDEX].normal_barcode.split('-')
                # print(len(normal_barcode_info))
                normal_barcode = normal_barcode_info[0] + "-" + normal_barcode_info[1] + "-" + normal_barcode_info[2]
                if tumor_barcode == normal_barcode:
                    pass
                else:
                    print("No Match")

                # Increase the variant caller index
                VAR_INDEX += 1

            # increase the row index
            i = i + 1
    # Return the variant callers to the calling function
    return VAR_CALLERS            


def generate_dsub(callers):
    # Generate the dsub instructions
    for caller in callers:
        dsub_instructions = ["dsub", "", "", "", ""]


if __name__ == "__main__":
    callers = main()
    f = open('matches.log', 'w')
    for caller in callers:
        caller.dump_caller_info_csv(f)
    
    f.close()

    # Determine reference for each

