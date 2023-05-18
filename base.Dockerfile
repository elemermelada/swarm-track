# Image based in python:slim
FROM python:slim AS tudatenv

# TODO - Do i need this here?
# Copy all files
WORKDIR /usr/src
COPY . .

# Update and install packages
RUN apt-get update && apt-get -y upgrade \
    && apt-get install -y --no-install-recommends \
    git \
    wget \
    g++ \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Conda stuff
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

# Download and install conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

# Update conda and create tudat environment
RUN echo "Running $(conda --version)" && \
    conda init bash && \
    . /root/.bashrc &&\
    conda update conda && \
    wget https://docs.tudat.space/en/latest/_downloads/dfbbca18599275c2afb33b6393e89994/environment.yaml && \
    conda env create -f environment.yaml && \
    conda activate tudat-space
