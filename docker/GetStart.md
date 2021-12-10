# Overview
## Docker Architecture
Docker uses a client-service architecture. The **Docker client** talks to the **Docker daemon**, which does the heavy lifting of building, running, and distributing you Docker containers. 

The **Docker client** and the **Docker daemon** can run on the same system, or you can connect a **Docker client** to a remote **Docker daemon**.

The **Docker client** and **Docker daemon** communicate using a **REST API**, over UNIX sockets or network interface.

![docker-architecture](./imgs/docker-architecture.svg)

## Docker Components
### Docker Daemon

Developers manage dockers through Docker API, and the Docker Daemon (dockerd) listens for the Docker API requests and manages Docker objects such as images, containers, networks, and volumes. A daemon can also communicated with other daemons to manage Docker services.

### Docker Client

The Docker client (docker) is the primary way that docker users interactive with Docker. For example, when you use a command such as ```docker run ...```, the client sends the command to **Docker Daemon** uses the Docker API. The Docker client can communicate with more than one daemon.

### Docker Registry

A Docker Registry stores Docker images. For example, Ducker Hub is a public docker registry that anyone can use. Docker is configured to look for Docker Hub for images by default. In addition, you can also run your own docker registry.

### Docker Images

A Docker image is a **Read-only** template with instructions for creating a docker container. You can create your own images or you can also use those created images by others in Docker registry.

To build your own images, you should create a **Dockerfile** with a simple syntax for defining the steps needed to create the image and run it. Each instructions in Dockerfile creates a layer in the image.

### Docker Containers

A Docker container is a runnable instance of a Docker image. You can create, start stop, remove a docker container using the Docker API or CLI. You can connect a container to one or more networks. 

You can build a Docker image based on a Docker container.

By default, a container is relatively well isolated from other containers and its host machine. You can control how isolated a container's network, storage, or other underlying subsystems are from other containers or from the host machine.

A Docker container is created from a Docker images, but any modification in the docker container won't change its image. And once you remove a docker container, any changes will disappear. Thus, you should remove containers carefully and you can also build a new image based on the container.

### Docker Objects

When you use docker, you are creating and using images, containers, networks, volumes, plugins, and other objects. These are all belongs to the concept of Docker objects.

# Get Docker
You can download and install docker on any operation systems, following [Get  Docker](https://docs.docker.com/get-docker/).

# Sample Application

We will use a web application as a example to better understand the basically features of Docker. The web application is about a **"Todo List"**, and you don't need to have any experience of web application development.

## Get the web application

[Download the App contents](https://github.com/docker/getting-started/tree/master/app). And you will see the ```package.json``` and two subdirectories (```src``` and ```spec```)

## Build the App's container image using Dockerfile

1. Create a file named ```Dockerfile``` in the same folder as the file ```package.json``` with the following contents:

   ```dockerfile
   FROM node:12-alpine
   RUN apk add --no-cache python g++ make
   WORKDIR /app
   COPY . .
   RUN yarn install --production
   CMD ["node", "src/index.js"]
   ```
   
2. Build the container image using the ```docker build``` command:

   ```shell
   docker build -t getting-started .
   ```

   The ```-t``` flag tags our image ```getting-started```

## Start an app container

1. Use the ```docker run``` command and specify the name of a image to start a container.

   ```shell
   docker run -dp 3000:3000 getting-started
   ```

   The ```-d``` flag means that we're running the docker container in "detached" mode (in the background). ```-p``` means we are mapping the host's port 3000 to the container's port 3000, and we can not to access the application without the port mapping.

2. Then, we can open the browser to http://locallhost:3000. And will see the application.

## Update the application
1. You can modify the Dockerfile or source code. For example, you can change the ```src/static/js/app.js``` file, update line 56 to use the new empty text:
```js
- <p className="text-center">No items yet! Add one above!</p>
+ <p className="text-center">You have no todo items yet! Add one above!</p>
```
Then you can rebuild a docker image by the command as:
```sh
docker build -t getting-started .
```

Then to start the a new container, but you probably saw an error about ```port is already allocated```.    This is because you have not stopped the container that created before.
2. You can also update the application directly in the docker container that created in last section ```Start an app container```. Then modify the source code in ```app.js```:

   ```
   # Get the ID of the connainer
   docker ps
   
   # Get into the docker and change the souce code.
   docker exec -it <container-id> sh
   
   vi src/static/js/app.js
   
   # modify the source code, and then exit to quit the container.
   ```

Refresh your browser and you should see your updated :

![](./imgs/todo-list-updated-empty-text.png)

## Push Your Image to Docker Registry
### 1. Make a docker image from docker container.

Once you stopped a docker container, all changes you have made will not be saved. So you can make a docker image to save it, so that you can even run it on a new host. The command of making a docker image from a container is:

```
docker commit <container-id> <repository-name>:<tag-name>

# for example: docker commit 78c3e9dc277d getting-started:latest
```

### 2.  Create a Repository on Docker Hub

1. Sign up or sign in to [Docker Hub](https://hub.docker.com/)

2. Click the **Create Repository** button, and choose a repository name by your self, such as ```test```

3. Then click the **Create** button.

### 3. Tag your local images' repository name the same as docker hub.

```
docker tag getting-started:latest <your-user-name>/<repository-name>:<tag-name>

# for example: docker tag getting-started:latest ielym/test:latest
```

Note that, if you want to push your local image to the docker registry, you have to tag the image according your username, your on-line repository name, but the tag-name ```latest``` you can define by your self.

### 4. Login Docker Account in Your Host.

1. To login you account in your local machine, by:

   ```sh
   docker login
   ```

2. Then follow the command line to input your username and password that according your docker hub.

### 5. Push the Image

```
docker push <your-user-name>/<repository-name>:<tag-name>

# for example: docker push ielym/test:latest
```

### 6. Run the Image on a New Instance

To setup a new computer or service instance with docker, and run:

```
docker run -dp 3000:3000 ielym/test:latest
```

Then you can open your browser and to get the new application.
