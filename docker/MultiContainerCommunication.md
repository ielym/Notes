# Multi containers

## Background

Now we have a **Todo List** web applications, and we also used a volume to persist the data. But how can we save our data in MySQL?

Of course you can run the MySQL in the same docker where the web app is in. But it's not recommend following **Each docker should do one thing and do it well**.

All right, let's run the MySQL in a separate container, a new question arisen : How to make a connection between the two containers? **The answer is networking**.

**Note : If two containers are on the same network, they can talk to each other. If they aren't, they can't.**

## Container networking

There are three default networking in docker for containers to communicate with each other. We can check them by :

```ls
docker network ls
```

| NETWORK ID   | NAME   | DRIVER | SCOPE |
| ------------ | ------ | ------ | ----- |
| 602fd938ad03 | bridge | bridge | local |
| 94e657bf94a7 | host   | host   | local |
| ab9d7d9f8631 | none   | none   | local |

### 1. Create a network

```sh
docker network create todo-app
```

### 2. Start a MySQL container

```sh
docker run -d \
     --network todo-app --network-alias mysql \
     -v todo-mysql-data:/var/lib/mysql \
     -e MYSQL_ROOT_PASSWORD=secret \
     -e MYSQL_DATABASE=todos \
     mysql:5.7
```

where :

+ ```-d``` means running detach (in background).
+ ```-v``` means mount the named volume ```todo-mysql-data``` to ```/var/lib/mysql```.
+ ```-e``` means environment variables setting.
+ ```--network``` means using the network ```todo-app``` that we created above.
+ ```--network-alias``` likes a static IP table lookup for container.

You will get a dive understanding of them in the following sections.

### 3. Running the MySQL container

```sh
docker exec -it <mysql-container-id> mysql -u root -p
```

Then, verify the databases:

```sql
show databases;
```
### 4. Check the networking

To use the MySQL container, we can check the networking informations of the mysql container using:

```sh
docker inspect <container-id>
```

>             "Networks": {
>                 "todo-app": {
>                     "IPAMConfig": null,
>                     "Links": null,
>                     "Aliases": [
>                         "mysql",
>                         "057563e538cf"
>                     ],
>                     "NetworkID": "aa4f0eac7f7e371a58389ee74187f4bcf5bd4edbcf59bd7e47a8eda765a605c2",
>                     "EndpointID": "8600e387c24a1e43e4197cb8bfb2eee17968dee6b165681ad09c0daf1801a981",
>                     "Gateway": "172.18.0.1",
>                     "IPAddress": "172.18.0.2",
>                     "IPPrefixLen": 16,
>                     "IPv6Gateway": "",
>                     "GlobalIPv6Address": "",
>                     "GlobalIPv6PrefixLen": 0,
>                     "MacAddress": "02:42:ac:12:00:02",
>                     "DriverOpts": null
>                 }
>             }

We can see the **Networks** is using ```todo-app```, and the **Aliases** is ```mysql```, also, we can get the ```Gateway```, ```IPAddress```, ```MacAddress``` etc. Your IP address is resolved to ```mysql```, that we set it by flag **--network-alias**, so docker was able to resolve it to the IP address of the container without to know what the real IP (172.18.0.2) is.

### 5. Connect to MySQL

We have create a MySQL container, and we have also verified it. So, how web application container could connect to it? Just through the command :

```
docker run -dp 3000:3000 \
   -w /app \
   -v $(pwd):/app \
   -e MYSQL_HOST=mysql \
   -e MYSQL_USER=root \
   -e MYSQL_PASSWORD=secret \
   -e MYSQL_DB=todos \
   node:12-alpine \
   sh -c "yarn install && yarn run dev"
```

Also, let's get to know what happened after we executed the command.

```-w``` defined the work directory. For example, ```python /home/test.py``` and with ```-w /home``` and ```python test.py```

```-v``` mount the ```$(pwd)``` to ```/app```

```-e``` configured the environment variables.

```node:12-alpine``` is the image.

`sh -c "yarn install && yarn run dev"`  We’re starting a shell using `sh` (alpine doesn’t have `bash`) and running `yarn install` to install *all* dependencies and then running `yarn run dev`. If we look in the `package.json`, we’ll see that the `dev` script is starting `nodemon`.

### 6. Run the web application with MySQL

+ Open the app in the browser and add a few items to your todo list.

+ Connect to the mysql database and prove that the items are being written to the database.

  ```sh
  docker exec -it <mysql-container-id> mysql -p todos
  
  select * from todo_items;
  ```

  

