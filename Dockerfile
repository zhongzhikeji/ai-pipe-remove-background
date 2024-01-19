FROM pytorch/pytorch:2.1.1-cuda12.1-cudnn8-runtime

LABEL maintainer='crapthings@gmail.com'

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /workspace

ADD https://huggingface.co/crapthings/inspyrenet-clothing/resolve/main/20240119/latest.pth .

COPY scripts ./scripts
COPY transparent-background ./transparent-background
COPY *.py .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN chmod +x ./scripts/install.sh
RUN ./scripts/install.sh
RUN python cache.py

RUN rm -rf ./scripts
RUN rm cache.py

CMD python -u ./runpod_app.py
