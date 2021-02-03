FROM tarekkma/python-dlib:latest

WORKDIR /root/app

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3","app.py"]