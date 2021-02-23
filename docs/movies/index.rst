.. _movies:

Movie management
================

After setting up a site including a staff gauge, configuring the camera, and providing cross sections, individual short
movies can be processed into surface flow velocities, and river discharge. Movies of 5 seconds at 1080p resolution
and 25 or 30 frames per second at 5Mbps bit rate are enough to yield good results. The process that OpenRiverCam
follows for this is displayed in the schematic below. The process can be run fully automated. At this stage we do not
yet offer interoperability in the processing of movie shots. We do offer the ability to inspect results of the
processing.

.. image:: ../img/movie_processing.png

The steps are as follows:

- Individual frames are extracted from the movie
- Each frame is corrected with the camera type's specific lens parameters, so that no distortions due to the lense
  shape appear in the frames
- Each frame is turned into a gray scaled. This is because Particle Image Velocimetry works with single-channel images
- Each frame is orthoprojected on a geographical plane using collected :ref:`Ground Control Points <gcp>` and the
  water level read out from the present staff gauge
- All frames are organised in frame-to-frame pairs, and velocities estimated from them. In the process, noisy and
  spurious velocity estimates are removed
- All valid frame-to-frame pair velocities are reduced to median, 5, 25, 75 and 95
  percentile velocity estimates. These are finally integrated to median, 5, 25, 75, 95 percentile river flow estimates
  using collected bathymetry data

The end result is a read out water level, combined with an estimated river flow over the cross section. In addition,
velocity estimates per frame pair, and for the 5 quantiles mentioned are available in OpenRiverCam's database.

Uploading a new video
---------------------

TODO

Assigning video to a location and camera configuration
------------------------------------------------------

TODO

Processing a new video
----------------------

TODO
