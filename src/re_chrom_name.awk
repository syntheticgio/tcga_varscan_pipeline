BEGIN{
FS="\t";
header=0;
}
{
if($2 == "SN:1") {gsub("SN:1","SN:chr1"); header=1;}
if($2 == "SN:2") {gsub("SN:2","SN:chr2"); header=1;}
if($2 == "SN:3") {gsub("SN:3","SN:chr3"); header=1;}
if($2 == "SN:4") {gsub("SN:4","SN:chr4"); header=1;}
if($2 == "SN:5") {gsub("SN:5","SN:chr5"); header=1;}
if($2 == "SN:6") {gsub("SN:6","SN:chr6"); header=1;}
if($2 == "SN:7") {gsub("SN:7","SN:chr7"); header=1;}
if($2 == "SN:8") {gsub("SN:8","SN:chr8"); header=1;}
if($2 == "SN:9") {gsub("SN:9","SN:chr9"); header=1;}
if($2 == "SN:10") {gsub("SN:10","SN:chr10"); header=1;}
if($2 == "SN:11") {gsub("SN:11","SN:chr11"); header=1;}
if($2 == "SN:12") {gsub("SN:12","SN:chr12"); header=1;}
if($2 == "SN:13") {gsub("SN:13","SN:chr13"); header=1;}
if($2 == "SN:14") {gsub("SN:14","SN:chr14"); header=1;}
if($2 == "SN:15") {gsub("SN:15","SN:chr15"); header=1;}
if($2 == "SN:16") {gsub("SN:16","SN:chr16"); header=1;}
if($2 == "SN:17") {gsub("SN:17","SN:chr17"); header=1;}
if($2 == "SN:18") {gsub("SN:18","SN:chr18"); header=1;}
if($2 == "SN:19") {gsub("SN:19","SN:chr19"); header=1;}
if($2 == "SN:20") {gsub("SN:20","SN:chr20"); header=1;}
if($2 == "SN:21") {gsub("SN:21","SN:chr21"); header=1;}
if($2 == "SN:22") {gsub("SN:22","SN:chr22"); header=1;}
if($2 == "SN:X") {gsub("SN:X","SN:chrX"); header=1;}
if($2 == "SN:Y") {gsub("SN:Y","SN:chrY"); header=1;}
if($2 == "SN:x") {gsub("SN:x","SN:chrX"); header=1;}
if($2 == "SN:y") {gsub("SN:y","SN:chrY"); header=1;}
if($2 == "SN:M") {gsub("SN:M","SN:chrM"); header=1;}
if($2 == "SN:MT") {gsub("SN:MT","SN:chrM"); header=1;}
if($2 == "SN:m") {gsub("SN:m","SN:chrM"); header=1;}
if($2 == "SN:mt") {gsub("SN:mt","SN:chrM"); header=1;}
print $0;
}
END
{
exit header
}
