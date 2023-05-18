# Image based in tudatenv
FROM tudat-space

# Copy all files
WORKDIR /usr/src
COPY . .
    
RUN echo 'conda activate tudat-space' >> /root/.bashrc
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
CMD ["python setup.py"]
