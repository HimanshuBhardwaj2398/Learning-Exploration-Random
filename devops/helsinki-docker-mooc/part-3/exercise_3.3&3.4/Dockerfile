FROM docker:25-git

RUN apk add --no-cache bash


COPY ./building.sh /usr/local/bin/building.sh


RUN chmod +x /usr/local/bin/building.sh


ENTRYPOINT ["/usr/local/bin/building.sh"]