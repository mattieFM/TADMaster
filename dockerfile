FROM oluwadarelab/tadmaster:latest

USER root:www-data

#install git so we can clone the repo
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y redis-server

#setup folder structure
RUN mkdir /var/www
RUN mkdir /var/www/html
RUN mkdir /var/www/html/Site

#set workdir
WORKDIR /var/www/html

#clone tadmaster repo
#we can either clone the repo or use the local copy, the local copy is more up to date hense why I am useing it
#RUN git clone https://github.com/OluwadareLab/TADMaster.git

#install dependancies

#copy web server files into image
COPY . /var/www/html/TADMaster

#copy both TADMaster and TADMaster plus run scripts
#COPY ./test_new.sh /var/www/html/TADMaster/test_new.sh
#COPY ./test.sh /var/www/html/TADMaster/test.sh
#COPY ./caller.sh /var/www/html/TADMaster/caller.sh
#COPY ./bed.sh /var/www/html/TADMaster/bed.sh

WORKDIR /var/www/html/TADMaster/Site

RUN pip3 install -r ./requirements.txt

EXPOSE 8000/tcp
EXPOSE 80/tcp

CMD ["/bin/bash", "-c", "/var/www/html/TADMaster/Site/run.sh"]