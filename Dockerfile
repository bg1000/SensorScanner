# Python Base Image from https://hub.docker.com/r/arm32v7/python/
FROM arm32v7/python:3.8.1-buster

# add required packages
RUN apt-get install git -y

# Download GarageQTPi app
RUN git clone https://github.com/bg1000/SensorScanner.git

# Intall required python modules
RUN pip3 install --no-cache-dir -r ./SensorScanner/requirements.txt

# Run GarageQTPi
CMD ["python3", "./SensorScnner/main.py"]
