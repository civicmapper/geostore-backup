A super-basic script for a local backup of AGOL/AGS services.

We run this script as a service on Windows via a `.bat` file, and dump the contents to Dropbox. Simple but effective for what we need it for.

# Requirements

* Python 2.7.x/Python 3.4 (https://www.python.org/)
* ArcGIS Desktop >= 10.2.x, w/ **ArcPy**
* Python ArcREST API (https://github.com/Esri/ArcREST) [release "July2015 v2"](https://github.com/Esri/ArcREST/releases/tag/FinalV2)
* numpy >= 1.7.1 (required by arcresthelper; numpy is included with ArcGIS default installation)
* six >= 1.1.0 ((required by arcresthelper)

# Installation

*Note: If you have not done so, you may need to add your python install path and scripts folder to your environment variables. In your system PATH environment variable, add both the path to Python and the Python Scripts folder. ex: `C:\Python27\ArcGIS10.4;C:\Python27\ArcGIS10.\Scripts`*

1. Install requirements
> `pip install -r requirements.txt`
2. run the `setup.py` for Python ArcREST from wherever you downloaded it. This should copy/install it to your python installation's `site-package` folder.
> `python setup.py install`

# Usage

Run from the command line:

```
python geostore_backup.py local\\path\\to\\save\\backups EsriUsername EsriPassword local\\path\\to\\backup.json
```

* `local\\path\\to\\save\\backups`: output path for backup
* `EsriUsername`: username for ArcGIS Online or ArcGIS Server on which the services to be backed up are located.
* `EsriPassword`: password for ArcGIS Online or ArcGIS Server on which the services to be backed up are located.
* `local\\path\\to\\backup.json`: location of a json file containing backup config parameters.

## The backup `json` config file

Use a json file to indicate the services and layers to be backed up. It should look like this:

```
{
    "Name of thing to be backed up":
    {
        "url": "http://services1.arcgis.com/vdNDkVykv9vEWFX4/ArcGIS/rest/services/Allegheny_County_Municipal_Boundaries/FeatureServer",
        "layers": [0]
    },
    "Name of other thing":
    {
        "url": "http://services1.arcgis.com/vdNDkVykv9vEWFX4/ArcGIS/rest/services/ZipCodes/FeatureServer",
        "layers": [0,2]
    },
}
```

`"Name of thing to be backed up"` (etc.) is the name given to the folder that will be created within the location you specify for storing you backups. It helps to make it short but obvious, e.g., "my_roads_layer"

`url` is the location of the service you want to back up.

`layers` is an array of numbers, mapping to the layers within the service endpoint. They must be explicitly specified.

## batch

A sample `.bat` file is included


# Caveats

> The Python ArcREST releases >= 3.0 break the createReplica function (or make it impossibly more difficult to use). This backup routine requires the "July2015 v2" (https://github.com/Esri/ArcREST/releases/tag/FinalV2).

> Right now this is only set up to authenticate to one ArcGIS Online or ArcGIS Server account at a time.
