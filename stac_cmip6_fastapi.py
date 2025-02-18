"""
Testing of the STAC FastAPI Interface for User Clients

Many clients and user scripts depend on the former ESGF RESTful API to search
and locate information about ESGF holdings. The UI/UX task team is looking to
understand how the next generation API is going to function to better scope the
work of updating user clients. While there are tools (such as pystac-client)
which can be used to programatically interact with the index, the consensus
among the task team is that it would be ideal if some replacement API was
available.

Being based on STAC, we do have a search endpoint:

https://api.stac.ceda.ac.uk/api.html

I can query (actually 'filter', recommended as 'query' is no longer being
developed) the CEDA endpoint for their CMIP6 data, but I am unable to filter by
CMIP6 properties which I can see as part of the response. I believe that the
below does not return any results because the CMIP6 properties are not in the
queryables for the collection:

https://api.stac.ceda.ac.uk/collections/cmip6/queryables

Is this because the CMIP6 extension is still a proposal?

https://github.com/stac-extensions/cmip6

At the moment, this appears to be a deadend.
"""

import json

import requests

# This works!
response = requests.post(
    "https://api.stac.ceda.ac.uk/search",
    json.dumps(
        {
            "filter": {
                "op": "and",
                "args": [
                    {"op": "=", "args": [{"property": "collection"}, "cmip6"]},
                ],
            }
        }
    ),
)
response.raise_for_status()
print(response.json()["numMatched"])

# Returns no matches
response = requests.post(
    "https://api.stac.ceda.ac.uk/search",
    json.dumps(
        {
            "filter": {
                "op": "and",
                "args": [
                    {"op": "=", "args": [{"property": "collection"}, "cmip6"]},
                    {"op": "=", "args": [{"property": "cmip6:variable_id"}, "rsus"]},
                ],
            }
        }
    ),
)
response.raise_for_status()
print(response.json()["numMatched"])
