FROM pytorch/pytorch:2.1.1-cuda12.1-cudnn8-runtime

LABEL maintainer='crapthings@gmail.com'

WORKDIR /workspace

COPY scripts ./scripts
COPY runpod_app.py .

RUN chmod +x ./scripts/install.sh
RUN ./scripts/install.sh
RUN python ./scripts/cache.py

RUN rm -rf ./scripts

CMD python -u ./runpod_app.py
