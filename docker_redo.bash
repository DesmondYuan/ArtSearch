# CLEAN UP
docker ps -a | awk '{ print $1,$2 }' |  awk '{print $1 }' | xargs -I {} docker rm -f {}
docker images | grep simplequery | awk '{print $3 }' | xargs -I {} docker rmi  {}
docker images | grep maindb | awk '{print $3 }' | xargs -I {} docker rmi  {}
docker network ls | grep appNetwork | awk '{print $1 }' | xargs -I {} docker network rm  {}

# RESTART
docker image build -t maindb -f maindb/Docker_db ./maindb
docker image build -t simplequery -f frontend/Docker_frontend ./frontend
docker network create appNetwork

# mount a persistent GCP volume
# docker run --name simplequery -d -p 5000:8081 -e DB_HOST=maindb -v /mnt/disks/ssd-disk/resource:/static --network appNetwork simplequery
# docker run --name maindb -d -v /mnt/disks/ssd-disk/resource:/static  --network appNetwork maindb
# sleep 2 && docker ps -a && docker logs simplequery && docker logs maindb 


# trying to mount local drive
docker run --name simplequery -d -p 5000:8081 -e DB_HOST=maindb --mount type=bind,source=/Users/debbieliske/Downloads/static,target=/static --network appNetwork simplequery
docker run --name maindb -d --mount type=bind,source=/Users/debbieliske/Downloads/static,target=/static --network appNetwork maindb
sleep 2 && docker ps -a && docker logs simplequery && docker logs maindb 
