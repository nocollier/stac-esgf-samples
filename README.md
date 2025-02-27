# stac-esgf-samples

The following represents my current best understanding with regards to what to
expect as ESGF moves to an implementation using STAC catalogs. The CMIP6 STAC
[extension](https://github.com/stac-extensions/cmip6) is also being developed
and so we may experience small changes as it matures. A CMIP7 extension will be
created as well when we have enough information about the schema.

## Big Changes

We will all have to learn how to submit a search request and unpack the
response, which I hope proves to be minimally painful. I think what could
possibly be more impactful to our tools are the following changes:

1. Dataset and File type records are gone. STAC lumps these together and calls
   it an `Item`. Ultimately this is a great change as it removes a lot of
   needless metadata replication. This makes the index smaller and ultimately
   faster to query. However, if your code was expecting a 2 phase query to first
   find your datasets and then the file information, you may have some
   refactoring to do.
2. There will be a single Item per `instance_id`. You will not see
   separate Items for the different locations from which you download the data (that is, by `dataset_id`).
   An Item will list in its `assets` all the files and locations from which they
   may be obtained. This also reduces metadata bloat, but could trigger a
   refactor in your tooling.
3. Indices will no longer be federated in the way they are now. Initially, there will be
   a US (West) and a UK (East) STAC index that are identical to each other, via
   a message queue. You will be able to point your tool at one of them and be
   sure that you have all the holdings worldwide. A limited number of modeling
   groups, data node operators will be given write access to this queue to
   publish messages as new data and/or locations become available.
4. The US-based Solr indices will be decomissioned "soon". While most of the
   team is working on the STAC implementation for CMIP7, we are also moving some
   projects (CMIP5, CMIP6, obs4MIPs, input4MIPs, etc.) into a
   ElasticSearch-based index (via Globus) which we are dubbing
   [ESGF-1.5](https://github.com/esgf2-us/esgf-1.5-design). This is to 'keep the
   lights on' for older data and allow the STAC catalogs to be developed
   unburdened by additional projects. The plan is to provide access to these
   holdings via an [API](https://github.com/esgf2-us/esg_fastapi) that matches
   the RESTful esg-search API as closely as possible. A lot of work is already
   done on this, intake-esgf uses test indices of this sort as defaults. If your
   tool would like to also be able to search for older projects and the index
   information was on a US index, then you will need to be able to handle
   requests from ESGF-1.5. As far as I know, other Solr indices in the federation
   are welcome to remain operational.

## What does a CMIP6 STAC Item look like?

This is taken from the
[examples](https://github.com/stac-extensions/cmip6/blob/main/examples/CMIP6.ScenarioMIP.UA.MCM-UA-1-0.ssp245.r1i1p1f2.Amon.psl.gn.v20190731.json)
of the CMIP6 STAC extension and subject to change. Initially you will see some high level meta-data which indentifies to which collection (aka project) the data belongs as well as some geometry directives. Most of our data is global and so these are less interesting, but in general STAC items can be search for by intersecting bounding boxes and so they must be listed here.

```json
{
  "type": "Feature",
  "stac_version": "1.0.0",
  "stac_extensions": [
    "https://stac-extensions.github.io/cmip6/v1.0.0/schema.json"
  ],
  "id": "CMIP6.ScenarioMIP.UA.MCM-UA-1-0.ssp245.r1i1p1f2.Amon.psl.gn.v20190731",
  "collection": "cmip6",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          -180,
          -88.28837585449219
        ],
        [
          176.25,
          -88.28837585449219
        ],
        [
          176.25,
          88.28837585449219
        ],
        [
          -180,
          88.28837585449219
        ],
        [
          -180,
          -88.28837585449219
        ]
      ]
    ]
  },
  "bbox": [
    -180,
    -88.28837585449219,
    176.25,
    88.28837585449219
  ],
  ...
  ```

You will also find a `properties` section where the expected CMIP6 facets may be found. They are prepended by a `cmip6:` to indicate that they are defined by the CMIP6 STAC extension. 

```json
  ...
  "properties": {
    "datetime": "2058-01-01T00:00:00Z",
    "start_datetime": "2015-01-17T00:00:00Z",
    "end_datetime": "2100-12-17T00:00:00Z",
    "access": [
      "HTTPServer"
    ],
    "latest": true,
    "replica": false,
    "retracted": false,
    "instance_id": "CMIP6.ScenarioMIP.UA.MCM-UA-1-0.ssp245.r1i1p1f2.Amon.psl.gn.v20190731",
    "citation_url": "http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.ScenarioMIP.UA.MCM-UA-1-0.ssp245.r1i1p1f2.Amon.psl.gn.v20190731.json",
    "cmip6:variable_long_name": "Sea Level Pressure",
    "variable_units": "Pa",
    "cf_standard_name": "air_pressure_at_mean_sea_level",
    "cmip6:activity_id": "ScenarioMIP",
    "cmip6:data_specs_version": "01.00.28",
    "cmip6:experiment": "update of RCP4.5 based on SSP2",
    "cmip6:frequency": "mon",
    "cmip6:further_info_url": "https://furtherinfo.es-doc.org/CMIP6.UA.MCM-UA-1-0.ssp245.none.r1i1p1f2",
    "cmip6:grid": "data reported on a model's native grid",
    "cmip6:grid_label": "gn",
    "cmip6:institution_id": "UA",
    "cmip6:mip_era": "CMIP6",
    "cmip6:source_id": "MCM-UA-1-0",
    "cmip6:source_type": "AOGCM",
    "cmip6:experiment_id": "ssp245",
    "cmip6:nominal_resolution": "250 km",
    "cmip6:table_id": "Amon",
    "cmip6:variable_id": "psl",
    "cmip6:variant_label": "r1i1p1f2",
    "levels": 0,
    "updated": "2024-02-20T19:28:19.804842Z",
    "created": "2024-02-20T19:28:19.804842Z"
  },
  ...
```

There is a `links` section which are used by the STAC software itself and likely not of any direct use to your tooling.

```json
  ...
  "links": [
    {
      "rel": "self",
      "type": "application/geo+json",
      "href": "https://api.stac.ceda.ac.uk/collections/cmip6/items/CMIP6.ScenarioMIP.UA.MCM-UA-1-0.ssp245.r1i1p1f2.Amon.psl.gn.v20190731"
    },
    {
      "rel": "parent",
      "type": "application/json",
      "href": "https://api.stac.ceda.ac.uk/collections/cmip6"
    },
    {
      "rel": "collection",
      "type": "application/json",
      "href": "https://api.stac.ceda.ac.uk/collections/cmip6"
    },
    {
      "rel": "root",
      "type": "application/json",
      "href": "https://api.stac.ceda.ac.uk/"
    }
  ],
  ...
```

Finally the `assets` are listed. At the moment only the CEDA assets are listed
in the test index. Furthermore, they have upload a
[kerchunk](https://fsspec.github.io/kerchunk/) reference file as well as https
access to the netcdf file. We will need to wait to see how they organize
multiple file locations in this reponse, but I am told they will follow the STAC
[alternate-assets](https://github.com/stac-extensions/alternate-assets)
extension.

```json
  ...
  "assets": {
    "reference_file": {
      "checksum": null,
      "checksum_type": null,
      "href": "https://dap.ceda.ac.uk/badc/cmip6/metadata/kerchunk/pipeline1/ScenarioMIP/UA/MCM-UA-1-0/kr1.0/CMIP6_ScenarioMIP_UA_MCM-UA-1-0_ssp245_r1i1p1f2_Amon_psl_gn_v20190731_kr1.0.json",
      "roles": [
        "reference",
        "data"
      ],
      "size": null,
      "type": "application/zstd",
      "open_zarr_kwargs": {
        "decode_times": true
      }
    },
    "data0001": {
      "href": "https://dap.ceda.ac.uk/badc/cmip6/data/CMIP6/ScenarioMIP/UA/MCM-UA-1-0/ssp245/r1i1p1f2/Amon/psl/gn/v20190731/psl_Amon_MCM-UA-1-0_ssp245_r1i1p1f2_gn_201501-210012.nc",
      "roles": [
        "data"
      ],
      "checksum": null,
      "checksum_type": null,
      "type": "application/netcdf",
      "time": "2015-01-01T00:00:00/2100-12-31T23:59:59",
      "area": [
        -180,
        -88.28837585449219,
        176.25,
        88.28837585449219
      ]
    }
  }
}
```