# Homelab `Jade` setup

Welcome to my homelab setup! This repository is a collection of Docker Compose configurations that I use to run all of my local services. I thought it might be helpful for some (even me when I move stuff around & lose configs lol), so decided to publish it here as a resource.

I run a `Dell PowerEdge R720XD` in my stack (named Jade!), alongside a 2-bay `UGREEN DXP2800`. Most of my services run on my PowerEdge.

![Homelab](./jade.png)

# NEW - Homelab IaC

I've built some new infra for my homelab - this time using Ansible w/ an Infrastructure as Code approach 😀

You can find my setup [here](https://git.alexav.gg/alex/homelab) for that.

## Docker

Evidently, I use Docker for a _lot_.

### How do I deploy?

I manage most of these file-based through a [code-server](./docker/code-server/) as I am relatively proficient in docker/docker-compose syntax, but if you are just starting out - I used [Portainer](https://portainer.io) for a while until I built up my Docker understanding. It provides a nice interface for managing Docker containers & stacks with good gitops integration.

### Networking

On my server (as you'll see in some of these configs), I use a custom `homelab` Docker network that the majority of my containers use. This allows me to both utilize hostnames in stuff like [Caddy](./docker/caddy/) & keep access to certain frontend services behind Tinyauth.

For containers that have multiple services (ie. an app that uses Postgres + Redis), I add an additional stack-specific network to segregate these, as usually they are container-specific & might conflict with other containers.

### `docker-compose` vs `docker compose`

At least on Ubuntu, the `docker-compose` apt package is _very_ outdated and finnicky. I have switched to using the Compose plugin from Docker. To install it, you'll have to

- Add Docker's official apt repository to your system [(docs)](https://docs.docker.com/compose/install/linux/#install-using-the-repository)
- Install the `docker-compose-plugin` package using your package manager
