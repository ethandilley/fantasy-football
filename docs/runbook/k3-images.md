Process for updating images in k3s.


# on pc
docker buildx build --platform linux/arm64 -t service:latest ./service
docker save service:latest -o service.tar
scp service.tar ethan@ethan.local:~/service.tar

# on server
sudo k3s ctr images import ~/service.tar
