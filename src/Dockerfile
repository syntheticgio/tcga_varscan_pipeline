FROM ubuntu:16.04

ENTRYPOINT ["/bin/bash", "pipeline.sh"]

RUN mkdir varscan

WORKDIR /varscan

COPY . /varscan

RUN chmod +x pipeline.sh

RUN apt-get update && apt-get -y install \
	build-essential \
	apt-utils \
	wget \
	default-jre \
	git \
	libncurses5-dev \
	zlib1g-dev \
	libbz2-dev \
	liblzma-dev \
	libcurl3-dev \
	time \
	python2.7 \
	python-pip

RUN pip install requests

RUN git clone https://github.com/dkoboldt/varscan.git

WORKDIR varscan
RUN ln -s VarScan.v2.4.0.jar VarScan.jar
WORKDIR /varscan
	
RUN wget https://github.com/samtools/samtools/releases/download/1.6/samtools-1.6.tar.bz2 && \
    tar -jxvf samtools-1.6.tar.bz2

WORKDIR samtools-1.6

RUN ./configure --prefix=/samtools/ && \
	make && \
	make install

WORKDIR /varscan

CMD ["-h"]
