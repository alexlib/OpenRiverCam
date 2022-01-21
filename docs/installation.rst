.. _installation:

Installation
============
Installation can be performed either on a server, or on your local machine. For deployment on the server, please contact
your system administrator to setup all components and establish a web location where you can access the tool. With a
server deployment, you can also add several processing nodes instead of just one, so that you can have multiple jobs
possibly initiated by multiple users running at the same time.

Installation locally
--------------------
The installation process on a local machine works with a docker-composition. Please go through the following steps for
a local installation

Install docker
~~~~~~~~~~~~~~
For this step, please follow the instructions for your operating system (Mac, Windows or Linux):

https://github.com/localdevices/OpenRiverCam/releases

For windows users, Docker desktop for Windows includes Docker-compose and so you will not
need the next step if you are on Windows.

Install Docker-compose
~~~~~~~~~~~~~~~~~~~~~~
Docker-compose is a method to run a number of Docker containers at the same time and arrange interactions between them.
Because OpenRiverCam consists of several components (web portal, database, back end, job queueing system), we use
Docker-compose to get all Docker container services running at the same time. To install Docker-compose, first get
Docker installed as per the instructions, then following these instructions:

https://docs.docker.com/compose/install/

.. note:: if you are on Windows, Docker-compose is included. This step can then be omitted.

Install OpenRiverCam
~~~~~~~~~~~~~~~~~~~~

Get the latest release of OpenRiverCam on

https://github.com/localdevices/OpenRiverCam/releases

Unzip the release to a folder. Then open a terminal in the folder where you unzipped the tool and type (after the prompt
indicated below with a $ sign).

.. code-block:: console

    $ docker-compose up

Updates
-------
Currently, we do not yet have a method to update the software automatically. We will implement this at a later stage.