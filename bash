# 1. First clean up everything
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker network rm speakup-network 2>/dev/null

# 2. Create a new network
docker network create speakup-network

# 3. Start the database container
docker run -d \
  --name db \
  --network speakup-network \
  -e POSTGRES_DB=speech_coach_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=RexDad_1 \
  postgres:15

# 4. Wait a few seconds for database to initialize
sleep 5


docker run -d \
  --name speakup-container \
  --network speakup-network \
  -p 8000:8000 \
  speakup

# 6. Check the logs
docker logs -f speakup-container