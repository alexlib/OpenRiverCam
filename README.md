# OpenRiverCam

## Installation
The Open River Cam software runs within a dockerized environment or can be deployed onto the cloud as separate services.

1. Install docker.  
More information: https://docs.docker.com/get-docker/.

2. Install docker-compose.  
More information: https://docs.docker.com/compose/install/.

3. Install Git.  
More information: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git.

4. Clone repository.  
Run "git clone https://github.com/TAHMO/OpenRiverCam.git" in your terminal.

## Usage
To run the software, simply run "docker-compose up" from the folder in which "docker-compose.yml" is located.
Interaction with services:
* OpenRiverCam dashboard is available at http://localhost
* MinIO storage dashboard is available at http://localhost:9000
* RabbitMQ Management interface is available at http://localhost:15672
* Postgres database is exposed at port 5432 and can be connected to with pgAdmin or any other PostgreSQL client.

Please note: it's strongly advised to change the default credentials in the ".env" file, especially when opening the ports for other machines.

## Examples
Example task for queue:
```json
{
  "type": "extract_snapshots",
  "kwargs": {
    "movie": {
      "file": {
        "bucket": "test-bucket",
        "identifier": "schedule_20201120_142304.mkv"
      }
    },
    "camera": {
      "name": "Foscam E9900P",
      "configuration": {},
      "lensParameters": {
        "k": 0.5
      }
    }
  }
}
```

Command to enter processing container shell:
```
docker exec -it hydrohub_processing_1 bash
```