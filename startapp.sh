docker build -t sweeft .

docker run --rm --detach --network=host --volume "$(pwd)":/usr/src/app --name sweeft sweeft
