Introduction
============
OpenRiverCam is a fully fledged professional software suite to allow for non-intrusive river flow monitoring with
cameras. The software provides the following features:

- manage river observation sites
- manage camera types and how they are configured on a site
- automatically convert movie shots into surface flow and river flow estimates
- establish rating curves from several observations

The entire methodology is meant to reduce the required fieldwork for river surveying and flow rating curve
management to a minimum. Only a small survey is needed for the bathymetry of the stream, and for orthoprojection of
the camera shots. This can be done during low flow conditions: safely, taking time, without exposure of equipment.

The software runs entirely on open-source libraries for its database, processing and front-end.

Methods
-------

.. image:: img/example_PIV.gif

The software's processing capabilities heavily rely on a scientific computer vision approach to estimate movements
from video called `Particle Image Velocimetry`. In the video above you can see what these methods do. A movie shot of
a few seconds is projected onto a geographical plane. Displacements of patterns are estimated from frame to frame.
Patterns that can be traced are for instance, debris floating by, or eddies in the water.
Spurious displacements or displacements that are not part of the stream are filtered out using automated filtering
methods. The resulting velocities can then be displayed on top of the movie frame. This video was taken at the Chuo
Kikuu stream, Dar es Salaam Tanzania. Using a measured cross section and the water level during the video, the
velocities can be integrated to a river flow.
For whom
--------
We intend this manual to be a how-to for hydrologists. The software is entirely web-based, and therefore,
the software can be used in three ways:

- by local installation on a laptop or desktop
- by installation on a server, allowing for central access by multiple users
- by use of our cloud service (in progress, please stay posted).

The software can be deployed using `docker`. For installation instructions, please refer to https://github.com/localdevices/OpenRiverCam/blob/master/README.md
If you are not familiar with `docker`, please ask your administrator to run the installation for you.

This manual
-----------
The remainder of this manual will go into all software components, including:

- :ref:`User administration <admin>`
- :ref:`Site management <sites>`
- :ref:`Camera configurations <cameras>`
- :ref:`Movie management <movies>`
- :ref:`Rating curve development <rating>`

We also provide a quick start :ref:`tutorial <tutorial>` with a real dataset, so that you can go through the steps
yourself and understand what the software can achieve within very limited time. We offer an :ref:`API description
<api>` in case you wish to perform background processing and know how to construct html API requests. We also provide
an extensive :ref:`field manual <survey>` for establishing and surveying a site

A typical workflow
------------------
We here describe very briefly the typical steps to establishing a site, process movies into velocities and river
flows, and finally, establish a rating curve from a collection of flow estimates. In the rest of the manual these
steps are elaborated upon in different subsections.

* Set up a camera at a fixed location, along with a staff gauge in view of camera. :ref:`Site choice <site_choice>`
* Perform a site survey (or redo if you believe the channel has changed significantly. Describe what needs to be
  measured, and why camera needs to remain fixed.
* insert site survey information to prepare site camera configuration, and cross-sections.
* Collect movies over a significant period during daytime, provide a water level to it
* Software automatically translates these into surface flow velocities and cross-section integrated discharge.
* Select H-Q points for rating curve analysis. Inspect results, go back to movies and reprocess if needed.
* Export rating curve results to .csv file

Acknowledgements
----------------
This software has been established as a fully free and open-source project through a project funded
by the World Meteorological Organisation - HydroHub, grant number PCTD/CO/000197/20
