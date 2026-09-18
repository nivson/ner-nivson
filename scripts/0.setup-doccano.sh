# This script is used to start a Doccano container for annotation tasks.
# It creates a Docker container with the necessary environment variables and volume for data persistence.

# Pull the Doccano image from Docker Hub
docker pull doccano/doccano

# Create a Docker container
docker container create --name doccano \
  -e "ADMIN_USERNAME=admin" \
  -e "ADMIN_EMAIL=admin@example.com" \
  -e "ADMIN_PASSWORD=password" \
  -v doccano-db:/data \
  -p 8000:8000 doccano/doccano
