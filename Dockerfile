# Image based in tudatenv
FROM tudatenv

# Copy all files
WORKDIR /home/devuser/src
COPY . .
USER root
RUN chown devuser:devuser -R .
USER devuser

# Append settings to .bashrc
RUN cat dev/bashrc.sh >> /home/devuser/.bashrc

# Run code from bash
ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
CMD ["/home/devuser/miniconda3/envs/tudat-space/bin/python setup.py"]