class TCGAVariantCaller(object):
    index = 0
    barcode = ""
    tumor_barcode = ""
    tumor_file = ""
    tumor_gdc_id = ""
    tumor_file_url = ""
    tumor_file_size = 0
    tumor_platform = ""
    normal_barcode = ""
    normal_file = ""
    normal_gdc_id = ""
    normal_file_url = ""
    normal_file_size = 0
    normal_platform = ""
    cancer_type = ""
    total_size = 0

    def __init__(self, index):
        self.index = index

    def set_index(self, index):
        self.index = index

    def set_barcode(self, barcode):
        self.barcode = barcode

    def set_tumor_barcode(self, tumor_barcode):
        self.tumor_barcode = tumor_barcode

    def set_tumor_file(self, tumor_file):
        self.tumor_file = tumor_file

    def set_tumor_gdc_id(self, tumor_gdc_id):
        self.tumor_gdc_id = tumor_gdc_id

    def set_tumor_file_url(self, tumor_file_url):
        self.tumor_file_url = tumor_file_url

    def set_tumor_file_size(self, tumor_file_size):
        self.tumor_file_size = float(tumor_file_size)

    def set_tumor_platform(self, tumor_platform):
        self.tumor_platform = tumor_platform

    def set_normal_barcode(self, normal_barcode):
        self.normal_barcode = normal_barcode

    def set_normal_file(self, normal_file):
        self.normal_file = normal_file

    def set_normal_gdc_id(self, normal_gdc_id):
        self.normal_gdc_id = normal_gdc_id

    def set_normal_file_url(self, normal_file_url):
        self.normal_file_url = normal_file_url

    def set_normal_file_size(self, normal_file_size):
        self.normal_file_size = float(normal_file_size)

    def set_normal_platform(self, normal_platform):
        self.normal_platform = normal_platform

    def set_cancer_type(self, cancer_type):
        self.cancer_type = cancer_type

    def set_total_size(self, total_size):
        self.total_size = total_size

    def dump_caller_info(self, f=None):
        print("---=== Debug Dump ===---")
        print("[ Index            ] {}".format(self.index))
        print("[ General Barcode  ] {}".format(self.barcode))
        print("[ Tumor Barcode    ] {}".format(self.tumor_barcode))
        print("[ Tumor File       ] {}".format(self.tumor_file))
        print("[ Tumor GDC ID     ] {}".format(self.tumor_gdc_id))
        print("[ Tumor File URL   ] {}".format(self.tumor_file_url))
        print("[ Tumor File Size  ] {}".format(self.tumor_file_size))
        print("[ Tumor Platform   ] {}".format(self.tumor_platform))
        print("[ Normal Barcode   ] {}".format(self.normal_barcode))
        print("[ Normal File      ] {}".format(self.normal_file))
        print("[ Normal GDC ID    ] {}".format(self.normal_gdc_id))
        print("[ Normal File URL  ] {}".format(self.normal_file_url))
        print("[ Normal File Size ] {}".format(self.normal_file_size))
        print("[ Normal Platform  ] {}".format(self.normal_platform))
        print("[ Cancer Type      ] {}".format(self.cancer_type))
        print("")

        if f:
            # Write output to log file
            try:
                f.write("[ Index            ] {}\n".format(self.index))
                f.write("[ General Barcode  ] {}\n".format(self.barcode))
                f.write("[ Tumor Barcode    ] {}\n".format(self.tumor_barcode))
                f.write("[ Tumor File       ] {}\n".format(self.tumor_file))
                f.write("[ Tumor GDC ID     ] {}\n".format(self.tumor_gdc_id))
                f.write("[ Tumor File URL   ] {}\n".format(self.tumor_file_url))
                f.write("[ Tumor File Size  ] {}\n".format(self.tumor_file_size))
                f.write("[ Tumor Platform   ] {}\n".format(self.tumor_platform))
                f.write("[ Normal Barcode   ] {}\n".format(self.normal_barcode))
                f.write("[ Normal File      ] {}\n".format(self.normal_file))
                f.write("[ Normal GDC ID    ] {}\n".format(self.normal_gdc_id))
                f.write("[ Normal File URL  ] {}\n".format(self.normal_file_url))
                f.write("[ Normal File Size ] {}\n".format(self.normal_file_size))
                f.write("[ Normal Platform  ] {}\n".format(self.normal_platform))
                f.write("[ Cancer Type      ] {}\n\n".format(self.cancer_type))
            except IOError:
                print("[ error ] Not able to write to log file!.")

    def dump_caller_info_csv(self, f, debug=False):
        total_size = self.tumor_file_size + self.normal_file_size
        if debug:
            print(
                "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(self.index, self.barcode, self.tumor_barcode,
                                                                           self.tumor_file, self.tumor_gdc_id,
                                                                           self.tumor_file_url, self.tumor_file_size,
                                                                           self.tumor_platform, self.normal_barcode,
                                                                           self.normal_file, self.normal_gdc_id,
                                                                           self.normal_file_url, self.normal_file_size,
                                                                           self.normal_platform, self.cancer_type,
                                                                           total_size))
        f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(self.index, self.barcode, self.tumor_barcode,
                                                                           self.tumor_file, self.tumor_gdc_id,
                                                                           self.tumor_file_url, self.tumor_file_size,
                                                                           self.tumor_platform, self.normal_barcode,
                                                                           self.normal_file, self.normal_gdc_id,
                                                                           self.normal_file_url, self.normal_file_size,
                                                                           self.normal_platform, self.cancer_type,
                                                                           total_size))

    def add_to_db(self, db="queued"):
        sqlstmt = "INSERT OR IGNORE INTO {} (" \
                  "tumor_barcode, tumor_file, tumor_gdc_id, tumor_file_url, tumor_file_size, " \
                  "tumor_platform, normal_barcode, normal_file, normal_gdc_id, normal_file_url, normal_file_size, " \
                  "normal_platform, cancer_type, total_size, tcga_id) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"," \
                  "\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"," \
                  "\"{}\",\"{}\")".format(db, self.tumor_barcode, self.tumor_file,
                                                  self.tumor_gdc_id, self.tumor_file_url,
                                                  self.tumor_file_size,
                                                  self.tumor_platform, self.normal_barcode, self.normal_file,
                                                  self.normal_gdc_id,
                                                  self.normal_file_url, self.normal_file_size,
                                                  self.normal_platform, self.cancer_type, self.total_size, self.barcode)
        return sqlstmt

    def populate_caller_with_row(self, row):
        self.set_barcode(row[1])
        self.set_tumor_barcode(row[2])
        self.set_tumor_file(row[3])
        self.set_tumor_gdc_id(row[4])
        self.set_tumor_file_url(row[5])
        self.set_tumor_file_size(row[6])
        self.set_tumor_platform(row[7])
        self.set_normal_barcode(row[8])
        self.set_normal_file(row[9])
        self.set_normal_gdc_id(row[10])
        self.set_normal_file_url(row[11])
        self.set_normal_file_size(row[12])
        self.set_normal_platform(row[13])
        self.set_cancer_type(row[14])
        self.set_total_size(row[15])
