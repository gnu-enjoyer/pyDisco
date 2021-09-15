FROM python:3

WORKDIR /pyDisco
ADD . /pyDisco

COPY "run.sh" .

RUN apt-get update && apt-get install -y \
  libffi-dev \
  python-dev \
    ffmpeg \
&& pip install -r requirements.txt && \
python setup.py build_ext --inplace && \
    chmod +x ./run.sh

ENTRYPOINT [ "./run.sh" ]