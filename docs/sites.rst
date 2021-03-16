.. _sites:

Site management
===============
Site management refers to adding new observation sites to your OpenRiverCam database. A `site` in OpenRiverCam is
nothing more than a rough location with a dedicated name of a site where you conduct river observations. It is also
the first thing you will need to do to get started with OpenRiverCam, as all other things depend on the site. To name
all dependencies in brief: once a site is established, you can add a camera configuration that belongs to that site.
This camera configuration holds more information on the type of camera on the site, the ground control points
measured on site, the area of interest within the camera objective and the resolution to which you want to project
the raw image frames. Any movie that is uploaded, is consequently labeled to a given camera configuration, and in
turn therefore also to a site.

To perform site management, first log in with your credentials. Then in the menu bar, click on `Setup`,
`Sites`.

.. image:: img/site_navigation.gif

In the Sites view there are several tabs you can select, being `List`, `Create`, and `With selected`.
The `List` tab is selected by default.

List
----
In the `List` tab you can see the already existing sites. If you are doing this the first time, you will see an empty
table with columns for `Site ID`, `Site name`, `EPSG code` and finally `Longitude [deg]` and `Latitude [deg]` for the
positions of monitoring sites. You will also see a map view of the world. If you have already added one or more
sites, then the table will hold all those sites, and the map view will automatically zoom to the extent that brings
all your existing sites in view. Below we provide a succinct explanation of the different columns that are used to
describe sites:

- Site ID: a number, automatically assigned to each site. The first site added will be given the number 1, the second
  2, etc.
- Site name: Your own name for the site. You can choose any recognizable name that works for your organisation.
- EPSG code: an EPSG code is a number, representing a `Coordinate Reference System` (CRS). A CRS describes how
  coordinates should be mapped onto the planet. Because the Earth has a spherical shape, a CRS that measures
  coordinates in West-East and North-South metres distances from a reference point, typically has a limited area where
  it is valid. For OpenRiverCam, we therefore need a CRS that is consequently used for all projections of Ground
  Control Points, the camera location, and the stream cross section. With a new site setup, a suitable CRS is
  automatically computed so in most cases you do not have to worry about this, unless you wish to use a very typical
  locally used CRS. Then you have to supply this actively.
- Latitude [deg]: the latitude location of a site measured in decimal degrees, measured from -90 degrees (South Pole)
  to 90 degrees (North Pole).
- Longitude [deg]: the longitude location of a site measured in decimal degrees, measured from -180 degrees (East) to
  180 degrees (East).

In the `List` tab, if you already have a site, you can view, edit or delete an individual site using the three icons
shown on the left side of the row in the table, displaying that site. If there are already camera configurations and
movies that belong to a selected site, then you cannot delete it anymore as that would also result in removal of
these movies and velocimetry results.

Create
------
To create a new site, navigate to the `Create` tab. You always have to type a unique name for your site. A
location only has to be approximate as it is not used for any computations, but just needed for situational awareness.
To select a location, OpenRiverCam provides two options:

- Fill in the latitude and longitude coordinates in decimal degrees in the appropriate fields on the page. Note that:

  - a latitude coordinate south (north) of the equator is negative (positive).
  - a longitude coordinate west (east) of the prime meridian is negative (positive).

- Click or drag the icon in the map to the location of interest. You can zoom in and out by scrolling or clicking the
  `+` and `-` signs on the map. You can also switch to a Google satellite or Google Terrain view, if this gives more
  situational awareness in your case. For instance, if you have a monitoring location on a bridge, but the bridge is
  not mapped in the default map layer OpenStreetMap, then a Google satellite view may help you.

A suitable EPSG code will be automatically computed when you enter a location's coordinates or select it through the
map. The code is a whole number, typically consisting of 5 digits. If you have a local coordinate reference system
that you know the EPSG code for, then you can also enter this manually yourself. If you are not familiar with EPSG
codes and coordinate reference systems, then we recommend to keep the automatically selected EPSG code.

When all the fields are filled in, click on `Save` to save and go back to the `List` tab, `Save and add another` to
save and add another site, or `Save and Continue Editing` to store the results and keep on editing them. If you wish
to go back to the `List` view without storing the result, simply click `Cancel`.

In the animation below, you can see an example of site creation for a possible site on the Ngwerere River in Lusaka -
Zambia.


.. image:: img/site_create.gif



With selected
-------------
The `With selected` tab is meant to perform operations on a set of selected sites. At this moment, the only
option provided here is to delete the selected sites. To do so, click on the check boxes left of the sites you wish
to remove, then click on `With selected` and then on `Delete`. You can also delete one individual site by using
the barrel icon, left of the the row containing the site information.

