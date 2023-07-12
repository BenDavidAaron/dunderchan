FROM python:3.11
WORKDIR /opt
COPY ./requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /opt/requirements.txt
COPY ./main.py /opt/main.py
COPY run-prod.sh /opt/run-prod.sh
CMD ["sh", "run-prod.sh"]
