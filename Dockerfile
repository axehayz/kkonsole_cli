FROM python:alpine

# Adding requirements file for python setup and installing requirements
COPY ./requirements.txt /kkonsole/config/

# Adding bash for Alpine doesn't carry it.
# RUN apk add --no-cache bash bash-completion
# Adding openssh for klookup
# RUN apk add --no-cache openssh
RUN apk add bash bash-completion && \
    pip install --upgrade pip && \
    pip install --trusted-host pypi.python.org -r /kkonsole/config/requirements.txt

# Change workdir to the application for relative path names inside container
WORKDIR /kkonsole

# Copy everything else needed
COPY *.py *.sh *.md /kkonsole/
COPY docs /kkonsole/docs
COPY kperform /kkonsole/kperform

# Run setup.py using pip to setup kkonsole script environment
RUN pip install --editable .

# Setup script for Click CLI commands auto-complete and (optionally) setup bash_profile
RUN ["/bin/bash","/kkonsole/auto-complete.sh"]

CMD ["/bin/bash"]