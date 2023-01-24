# pull official base image
FROM python:3.10

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


# copy project
COPY . /app/

# install the two necessary fonts
RUN mkdir -p /usr/share/fonts/truetype/
RUN install -m644 ./static/fonts/AgencyFB-Bold.ttf /usr/share/fonts/truetype/
RUN install -m644 ./static/fonts/Tahoma.ttf /usr/share/fonts/truetype/

# install ffmpeg and imagemagick
RUN apt-get update && apt-get upgrade -y && apt-get install -y ffmpeg && apt-get install -y imagemagick

# copy changed configurarion files to the imagemagick directory
RUN cp ./imagemagick/policy.xml /etc/ImageMagick-6/policy.xml

ENTRYPOINT ["gunicorn", "--timeout", "300", "-b", "0.0.0.0:5042", "--access-logfile", "-", "--error-logfile", "-", "app:app"]

EXPOSE 5042