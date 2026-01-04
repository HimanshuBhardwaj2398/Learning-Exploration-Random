FROM alpine:3.21

WORKDIR /usr/src/app

COPY hello.sh .

RUN touch additional.txt

RUN chmod +x hello.sh

CMD ["./hello.sh"]