FROM ubuntu:latest
MAINTAINER Hikari<contact@hikari.bond>
VOLUME /opt/HikariServerLauncher
WORKDIR /
RUN apt-get update
ADD main.bin /data/main.bin
EXPOSE 25565
ENV PYTHONIOENCODING=utf-8
CMD ["/data/main.bin"]