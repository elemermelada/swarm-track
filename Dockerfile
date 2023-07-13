# Image based in tudatenv
FROM tudatenv

# Copy all files
WORKDIR /usr/src
COPY . .

# Append settings to .bashrc
RUN echo 'conda activate tudat-space' >> /root/.bashrc
RUN cat dev/bashrc.sh >> /root/.bashrc

# Run code from bash
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
CMD ["python setup.py"]
