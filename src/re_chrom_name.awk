BEGIN{
FS="\t";
}
{
if($2 == "SN:1") {gsub("SN:1","SN:chr1");}
if($2 == "SN:2") {gsub("SN:2","SN:chr2");}
if($2 == "SN:3") {gsub("SN:3","SN:chr3");}
if($2 == "SN:4") {gsub("SN:4","SN:chr4");}
if($2 == "SN:5") {gsub("SN:5","SN:chr5");}
if($2 == "SN:6") {gsub("SN:6","SN:chr6");}
if($2 == "SN:7") {gsub("SN:7","SN:chr7");}
if($2 == "SN:8") {gsub("SN:8","SN:chr8");}
if($2 == "SN:9") {gsub("SN:9","SN:chr9");}
if($2 == "SN:10") {gsub("SN:10","SN:chr10");}
if($2 == "SN:11") {gsub("SN:11","SN:chr11");}
if($2 == "SN:12") {gsub("SN:12","SN:chr12");}
if($2 == "SN:13") {gsub("SN:13","SN:chr13");}
if($2 == "SN:14") {gsub("SN:14","SN:chr14");}
if($2 == "SN:15") {gsub("SN:15","SN:chr15");}
if($2 == "SN:16") {gsub("SN:16","SN:chr16");}
if($2 == "SN:17") {gsub("SN:17","SN:chr17");}
if($2 == "SN:18") {gsub("SN:18","SN:chr18");}
if($2 == "SN:19") {gsub("SN:19","SN:chr19");}
if($2 == "SN:20") {gsub("SN:20","SN:chr20");}
if($2 == "SN:21") {gsub("SN:21","SN:chr21");}
if($2 == "SN:22") {gsub("SN:22","SN:chr22");}
if($2 == "SN:X") {gsub("SN:X","SN:chrX");}
if($2 == "SN:Y") {gsub("SN:Y","SN:chrY");}
if($2 == "SN:x") {gsub("SN:x","SN:chrX");}
if($2 == "SN:y") {gsub("SN:y","SN:chrY");}
if($2 == "SN:M") {gsub("SN:M","SN:chrM");}
if($2 == "SN:MT") {gsub("SN:MT","SN:chrM");}
if($2 == "SN:m") {gsub("SN:m","SN:chrM");}
if($2 == "SN:mt") {gsub("SN:mt","SN:chrM");}
print $0;
}
