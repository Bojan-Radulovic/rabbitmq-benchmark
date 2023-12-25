# rabbitmq-benchmark
A simple Flask app for messuring the performanse impact of adding aditional subcribers to a system that uses the RabbitMQ message broker.
## Table of contents
- [rabbitmq-benchmark](#rabbitmq-benchmark)
  - [Table of contents](#table-of-contents)
  - [General info](#general-info)
  - [Technologies](#technologies)
  - [Use](#use)
## General info
This project was created as a part of my "Infrastructure for large-scale data" university course. It presents users with a simple interface for running a benchmark test on a system that uses the RabbitMQ message broker.
## Technologies
* Python 3.9.5
* Docker
* Flask
* RabbitMQ
* MongoDB
* ab - Apache HTTP server benchmarking tool
* ...
## Use
To successfully initiate the project, it is necessary to follow these steps:
1) Clone the project from GitHub to your local machine.

2) Open a terminal in the project's root directory.

3) Execute the command `docker-compose up --scale app-worker=<N>` where \<N\> is the desired number of worker components (subscribers).

4) Wait for the system to initialize. The system is initialized when the rabbitmq component outputs the message "Server startup complete" and when the app-web component reports that the server is running (Running on http://127.0.0.1:5000).

5) Access the server using a web browser at the link http://127.0.0.1:5000.

6) Use the interface to initiate performance testing with the desired parameters by clicking the "Start Benchmarking" button.

