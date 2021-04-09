.. _tutorial:

Quick start
===========

To get you started with the software quickly, this section goes through all functionalities with an example package of data.
You can download this package in a zip-file from the following link: ZIP-FILE. The zip-file contains all the sample
data sets, including survey data and some sample videos to get you started. It should take you about XXXX minutes to
complete this tutorial.

We assume that you have a user login for the tool and that you have a deployment that you can go to, either on your
local computer or on a provided web server. In case you have a locally deployed version using the Docker image,
please open a browser and type `localhost` in the browser window and login with your credentials. If your system
administrator has installed a web server deployment then please ask for the correct website to go to. We use Google
Chrome throughout our tutorial. Below you see the expected result.

.. image:: img/landing_page.png

.. _tutorial_site_setup:

setup a new site
----------------

For this tutorial we assume that a new camera has been installed on a new site, and that all required surveying has
been performed. For a manual on surveying, please refer to the :ref:`survey manual <survey>`. Therefore, we need to
establish a new site location and a new camera type and a new camera, of that camera type, belonging to the site
installation. Let's start with making a new site.

First select `Setup`, then `Sites`. You will see an empty list and empty world map, because you have not yet made any
sites yet. Now click on `Create`, and fill in the following details:

- Site name: Chuo Kikuu - Senga Road
- Longitude: 39.2522
- Latitude: -6.7692

The EPSG code will automatically be selected. Please keep the suggested number as is. Once the numbers are filled
out, you should see a marker on Dar es Salaam, on the Chuo Kikuu stream. You can zoom in and out to better inspect
the location. You can change the background map layers to see satellite or terrain views. You should see a view as
shown below. If you are satisfied, please click `Save` to go back to the list view. You will here see the site in the
world map as well.

.. image:: img/tutorial_site.png

For more information on creating a new site, please go to :ref:`Site management <sites>`.

Add a new camera type
---------------------
We are going to use a Foscam F19901 EP camera. We will add this camera type and its intrinsic lens characteristics to
our database. To do this, select `Setup`, `Camera types`, `Create`. Fill out the following details:

- Camera name: Foscam F19901EP
- k1 barrel distortion [-]: -3e-6
- c Optical center [-]: 2
- f Focal length [mm]: 4

Click and `Save` and you should see a message that the record was successfully created, and the list view with your
new camera type, as below.

.. image:: img/tutorial_camera_type.png

Add a bathymetry
~~~~~~~~~~~~~~~~
Now we will provide the bathymetry, that was measured during the survey on this site. Please go to `Setup`,
`Bathymetry`, and then choose `Create`. First you have to select for which site you wish to provide bathymetry, and
a time stamp. This is meant to ensure you can provide a new bathymetry in case the profile has been significantly
changing due to erosion and or sedimentation, or because you wish to use a profile that is over a part of the
objective that has more favourable conditions for particle image velocimetry, e.g. due to light conditions.

Once you have select a site and time stamp, you can provide bathymetry. We will choose a very fast method to provide
bathymetry, by giving a set of comma separated values in longitude, latitude, elevation format, and the EPSG code
above it. The EPSG code for regular latitude longitude is 4326. To do this simply open the provided file
`cross_section.csv` in a text editor. Please do not use excel or word, but a flat text editor such as textpad,
notepad++ or your own favorite editor. Copy-paste the entire contents into the text area where indicated, and click
on `Store CSV`. Accept the warning message, and you will be brought to the details page that shows the site location,
with the spatial coordinates of the profile points, and a plot of the bathymetry from left to right bank. Below you
can see this result.

.. image:: img/tutorial_bathymetry.png

Add a new camera
----------------
Now we want to add a camera, that is located at a specific site. Go to `Setup`, `Cameras on sites`, `Create`. Now
select the site, and select which camera type you have on this site. We currently only have one for both, so the
selection is quite easy. Also select the status. The camera is active, meaning that you should select
`CAMERA_STATUS_ACTIVE` as a state. Again click on `Save` to continue, and see the result.

Camera configuration
------------------------------
Now we go to a more extensive configuration part. The camera configuration. Here we have to provide the information
of the survey, and define the window size of the velocimetry methods we want to use. This setup has several parts,
that we will go through one by one.

Add a new camera configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First click on `Setup`, `Camera configuration`, `Create`. Now you have to select for which camera, you wish to
provide a configuration. We are doing this for the camera we just created in the previous step. Select this camera
and click `Save` to continue. You now have an empty camera configuration. This needs to be edited in the following
steps.

Camera config step 1:
~~~~~~~~~~~~~~~~~~~~~
To go to the first configuration step, click on the `Edit` button, left of the new camera configuration, as shown in
the image below.

.. image:: img/tutorial_cameraconfig_edit.png

A new screen will be shown where you can insert the following:

- Time Start: this is the start time of the period in which the camera configuration is valid. If you change the
  orientation of the camera or anything else, then you have to make a new camera configuration and ensure the old one
  becomes invalid and the new one receives a start time commensurate with the validity period. Select for instance
  today as a Time Start value
- Time End: Here select any day in the future. This is the end time of the period in which this configuration is
  valid. After this period, you may install for instance a new camera, or alter the angle or anything else about the
  camera configuration.
- File: here we need to provide a sample movie in which the ground control points are visible, taken during the
  survey period. Here, select the video `control_point.mkv` from the tutorial Zipfile.

Once all fields are provided, click on `Save`. You should see a `Please wait` page. After a short while, you are
redirected to a new page where you can provide the survey information. Please open the file "survey.txt". This file
contains all information you need to provide. You will also need to click on the different ground control points. If
you look carefully at the ground control points snapshot, you will see that there are 4 sticks in the water. Below
the sticks are marked with red dots, at the place where they enter the water. These are your ground control points.
Please do the following:

- click on all four ground control points
- fill out the right coordinates with the right the ground control point, looking at the color coding. The
  coordinates are provided in the table below.

=============  ================  ================
Control point  Coordinate X [m]  Coordinate Y [m]
=============  ================  ================
bottom-left    527862.67         9251760.47
bottom-right   527870.45         9251761.85
top-right      527871.16         9251764.63
top-left       527861.12         9251763.74
=============  ================  ================

Fill out the following water levels:

Height of water level in coordinate system [m]: -17.50
Staff gauge water level during taking of the gcp points [m]: 0.1

.. note:: the first water level value is the level during the survey, within the used coordinate reference system.
   The second value is the value that is read from the staff gauge in view. Within this example the staff gauge was
   not yet finalized. It has been read from a later snapshot.

Below that, click on four points in the right order, to identify the area of interest. The order is important. First
click on the top-left part which is the upstream left-bank, then the top-right (downstream left-bank), then
bottom-right, and finally bottom-left. You should have something as shown below. If you want to remove a wrongly
selected point, then right-click on it.

.. image:: img/tutorial_aoi.png

Then fill out the location of the camera in the used coordinate reference system as follows:

Lens coordinate X [m]: 527869.47
Lens coordinate Y [m]: 9251757.48
Lens coordinate Z [m]: -14.38

Pixel size can be set at 0.01 m.

Click on `Next`.

Provide camera lens position
----------------------------


.. _tutorial_movie_process:

Process a new movie
-------------------

TODO


.. _tutorial_rating:

Establish a rating curve
------------------------

TODO
