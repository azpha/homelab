# Homelab `Jade` setup

Welcome to my homelab setup! This repository is a collection of Docker Compose configurations that I use to run all of my local services. I thought it might be helpful for some (even me when I move stuff around & lose configs lol), so decided to publish it here as a resource.

I run a `Dell PowerEdge R720XD` in my stack (named Jade!), alongside a 2-bay `UGREEN DXP2800`. Most of my services run on my PowerEdge.

![Homelab](./jade.png)

## Docker

Evidently, I use Docker for a _lot_. I manage most of these file-based as I am relatively proficient in docker/docker-compose syntax, but if you are just starting out - I used [Portainer](https://portainer.io) for a while until I built up my Docker understanding. It provides a nice interface for managing Docker containers & stacks.

### `docker-compose` vs `docker compose`

At least on Ubuntu, the `docker-compose` apt package is _very_ outdated and finnicky. I have switched to using the Compose plugin from Docker. To install it, you'll have to

- Add Docker's official apt repository to your system [(docs)](https://docs.docker.com/compose/install/linux/#install-using-the-repository)
- Install the `docker-compose-plugin` package
