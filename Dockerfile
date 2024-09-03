FROM guswns531/montage-func

USER root

# RUN apt update && \
#     apt install -y wget

RUN cp lib/* /usr/lib/x86_64-linux-gnu/

USER 1002:1000

# docker build -t guswns531/montage-func:v2 .
# docker push guswns531/montage-func:v2