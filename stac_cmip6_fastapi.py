"""
Using the STAC FastAPI to query the index.

Because we are using STAC, there are already SDKs for languages that our tools
use (python, Javascript, Java). I will show here how to query, but it might be
better to look into using the appropriate SDK in the native language of your
application.

You will see a `query` keyword, but this is not recommended by STAC. It is light
on features and the language is one of their invention. In contrast, `filters`
has many features and uses the Common Query Language
[CQL2](https://docs.ogc.org/is/21-065r2/21-065r2.html) to compose logical
operators.

NOTE: For the moment, if you want to query a property in the CMIP6 extension, it
must be prefixed by `properties.`. This is not the desired behavior and will be
[fixed](https://github.com/stac-extensions/cmip6/issues/9).
"""

import json

import requests

# look for CMIP6 data for either rsus or rsds
response = requests.post(
    "https://api.stac.ceda.ac.uk/search",
    json.dumps(
        {
            "filter": {
                "op": "and",
                "args": [
                    {"op": "=", "args": [{"property": "collection"}, "cmip6"]},
                    {
                        "op": "or",
                        "args": [
                            {
                                "args": [
                                    {"property": "properties.cmip6:variable_id"},
                                    "rsus",
                                ],
                                "op": "=",
                            },
                            {
                                "args": [
                                    {"property": "properties.cmip6:variable_id"},
                                    "rsds",
                                ],
                                "op": "=",
                            },
                        ],
                    },
                ],
            },
        }
    ),
)
response.raise_for_status()
print(response.json()["numMatched"])
# 806
