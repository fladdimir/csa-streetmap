# Dockerfile for test execution 

FROM python:3.7-stretch
WORKDIR /usr/src
# prerequisite for rtree (osmnx)
RUN apt-get update && apt-get install -y libspatialindex-dev
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
