
# Setup
On linux, use Docker to build and run the image as follows (replacing `<some-name>` with a name of your choice):

```bash
$ docker build -t <some-name> .
Sending build context to Docker daemon  1.443GB
Step 1/9 : FROM ubuntu:latest
...
Successfully tagged <some-name>:latest
$ docker run -itv `pwd`/data:/code/data <some-name>
wget -P data -Nc "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2017.csv"
...
all success
```

This will build the image (if not already built) start the download of the raw data (if not already done) into the folder `data` inside the current directory in the host.