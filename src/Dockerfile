FROM ubuntu:16.04

#ENTRYPOINT ["/bin/bash", "pipeline.sh"]

WORKDIR /varscan

COPY . /varscan

RUN apt-get update && apt-get -y install \
	build-essential \
	wget \
	default-jre \
	git \
	libncurses5-dev \
	zlib1g-dev \
	libbz2-dev \
	liblzma-dev \
	libcurl3

RUN git clone https://github.com/dkoboldt/varscan.git

WORKDIR varscan
RUN ln -s VarScan.v2.4.0.jar VarScan.jar
WORKDIR /varscan
	
RUN wget https://github.com/samtools/samtools/releases/download/1.6/samtools-1.6.tar.bz2 && \
    tar -jxvf samtools-1.6.tar.bz2

WORKDIR samtools-1.6

RUN ./configure --prefix=/samtools/bin/ && \
	make && \
	make install

WORKDIR /varscan

CMD ["-h"]
