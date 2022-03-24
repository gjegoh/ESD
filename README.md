# Digitalize Tuition Records

# Business Scenario
Tuition centres in Singapore rely on tedious manual processes to enrol students, schedule classes, distribute workload among tutors and collect payment. This often leads to a loss in revenue due to the extra manpower required to carry out these processes. 

Furthermore, tutors often lack the ability to choose their preferred class schedules and lack flexibility in deciding on their preferred workload, leading to unhappiness among tutors and a barrier to entry for many aspiring tutors.

# Solution 
We aim to digitally transform the traditional tuition centres, eliminating the majority of manual work required from both parties by streamlining and automating majority of the processes. 

Additionally, we would also provide the ability and flexibility for tutors to decide on their own schedule and workload easily, within the constraints of their contract. Thereby, making it more appealing to both new and existing tutors.

This will be done via a UX-first approach, through the use of our web application that can be easily accessed and utilized by all stakeholders. Furthermore, it will be deployable for any tuition centre as their enterprise solution.

# Database connections on RDS
Database_connection URL = studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com
port_no = 3306
hostname = admin
password = thisismypw

# Mailchimp (use postman to send requests):
1. select authorization
2. enter username and password
  - Username: jenniferwxe
  - Password: 149218c56ba8c2f24e05f157add74e6b-us14


# Technologies and features

- [x] Python & Flask & MySQL Database
- [x] Stripe Subscriptions (Create, Cancel, Reactivate, Update supported)
- [x] HTML theme 
- [x] Docker: Fully split into microservices. Runs with Docker Compose, but can **[easily be translated to Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/)**
- [x] User sign up and login (Email Address)
- [x] Notifications for users (Student, Tutor and Admin)

# How To Run The Application (After Installation)

You should make sure that your database is running first and foremost, else the following will fail. Look under installation for Windows or Mac/Linux for how to run the database locally. It just needs to be running in the background, all the databases and tables are created programmatically.

1. Simply navigate (in a terminal) into the ~/app folder.
2. Run `docker-compose build` for your first build and when you have made changes.
3. Run `docker-compose up` to run all the services.

Please configure `~/app/setup_app/config.py` as needed. I recommend making a mode for development and production (staging if necessary) with all the needed credentials. The file is very easy to extend with new config secrets.

Note that scaling is very easy, you can just convert your `docker-compose.yml` file to Kubernetes files, and you can easily get set up and running in Google Cloud Platform or Amazon Web Services. [Read this tutorial for more](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/).

# Microservices

1. studentMS.py - Port 5001
2. tutorMS.py - Port 5002
3. adminMS.py - Port 5003
4. classMS.py - Port 5004
5. classSchedule.py - Port 5005
6. NotificationMS.py - Port 5006
7. stripeMS.py - Port 5007

