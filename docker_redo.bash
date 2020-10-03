# CLEAN UP
docker ps -a | awk '{ print $1,$2 }' |  awk '{print $1 }' | xargs -I {} docker rm -f {}
docker images | grep simplequery | awk '{print $3 }' | xargs -I {} docker rmi  {}
docker images | grep maindb | awk '{print $3 }' | xargs -I {} docker rmi  {}
docker network ls | grep appNetwork | awk '{print $1 }' | xargs -I {} docker network rm  {}

# RESTART
docker image build -t maindb -f maindb/Docker_db ./maindb
docker image build -t simplequery -f frontend/Docker_frontend ./frontend
docker network create appNetwork
#docker run --name maindb -d --network appNetwork maindb
#docker run --name simplequery -d -p 5000:8081 -e DB_HOST=maindb --network appNetwork simplequery

# trying to mount local drive
docker run --name simplequery -d -p 5000:8081 -e DB_HOST=maindb --mount type=bind,source=/home/byuan/proj1/working_dir/ArtSearch/resource,target=/resource --network appNetwork simplequery
docker run --name maindb -d --mount type=bind,source=/home/byuan/proj1/working_dir/ArtSearch/resource,target=/resource --network appNetwork maindb
sleep 2 && docker ps -a && docker logs simplequery && docker logs maindb 
