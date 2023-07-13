# Image based in python:slim
FROM python:latest AS tudatenv

# Update and install packages
RUN apt-get update && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
    git \
    wget \
    g++ \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add devuser to avoid using 
RUN addgroup --gid 1000 devuser
RUN adduser --disabled-password --gecos "" --home /home/devuser --uid 1000 --gid 1000 devuser
ENV HOME /home/devuser
USER devuser
WORKDIR /home/devuser

# Conda stuff
ENV PATH="/home/devuser/miniconda3/bin:${PATH}"
ARG PATH="/home/devuser/miniconda3/bin:${PATH}"

# Download and install conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /home/devuser/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Update conda and create tudat environment
RUN conda init bash && \
    . /home/devuser/.bashrc &&\
    conda update conda && \
    wget https://docs.tudat.space/en/latest/_downloads/dfbbca18599275c2afb33b6393e89994/environment.yaml && \
    conda env create -f environment.yaml