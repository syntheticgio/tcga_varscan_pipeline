import csv

dict_buckets = {}
list_buckets = []

# with open("new_matches_all.csv", "w") as match_writer:
#     csv_writer = csv.writer(match_writer, delimiter=",")
i = 0
with open("matches_all.csv", "r") as matches:
    csv_reader = csv.reader(matches, delimiter=",")
    for row in csv_reader:
        i += 1
        # row[1] = tcga id
        # row[2] = sample 1 full tcga ID
        # row[6] = sample 1 gs bucket location
        # row[9] = sample 2
        # row[12] = sample 2 gs bucket location
        with open("updated_download_list.csv", "r") as f:
            new_reader = csv.reader(f, delimiter=",")
            next(new_reader)
            for new_row in new_reader:
                if new_row[10] == row[2]:
                    # update sample 1
                    # print("Replacing {} with {}".format(row[5], new_row[45]))
                    row[5] = new_row[45]
                    bucket = "gs://" + new_row[45].split("/")[2]
                    list_buckets.append(bucket)
                    if bucket in dict_buckets:
                        dict_buckets[bucket] += 1
                    else:
                        dict_buckets[bucket] = 1
                    break
                elif new_row[10] == row[8]:
                    # update sample 2
                    # print("Replacing {} with {}".format(row[11], new_row[45]))
                    row[11] = new_row[45]
                    bucket = "gs://" + new_row[45].split("/")[2]
                    list_buckets.append(bucket)

                    if bucket in dict_buckets:
                        dict_buckets[bucket] += 1
                    else:
                        dict_buckets[bucket] = 1
                    break
        # csv_writer.writerow(row)
        print("Row # {}\r".format(i), end="")
    print("\n")
    print(dict_buckets)
    # print(list_buckets)
