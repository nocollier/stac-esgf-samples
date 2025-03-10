import pandas as pd
from pystac_client import Client, ItemSearch


def search_cmip6(
    base_url: str, items_per_page: int = 100, **search_facets: str | list[str]
) -> ItemSearch:
    """
    Returns a STAC client item search filtered by the search facets.

    Parameters
    ----------
    base_url : str
        The URL of the STAC API.
    items_per_page : int, optional
        The number of items to return per page.
    **search_facets : str, list[str]
        The traditional search facts expressed as additional keyword arguments,
        for example `variable_id=['tas','pr']` or `source_id='UKESM1-0-LL'`.

    Returns
    -------
    ItemSearch
        The STAC search results.

    NOTE: This helper function assumes that the facet you wish to query is in
    the list of `cmip6` properties of the STAC CMIP6 extension.
    """
    client = Client.open(base_url)
    cql_filter = {
        "op": "and",
        "args": [
            {
                "op": "in",
                "args": [
                    {"property": f"properties.cmip6:{facet}"},
                    facet_values if isinstance(facet_values, list) else [facet_values],
                ],
            }
            for facet, facet_values in search_facets.items()
        ],
    }
    results = client.search(
        collections="cmip6", limit=items_per_page, filter=cql_filter
    )
    return results


def to_dataframe(items: ItemSearch) -> pd.DataFrame:
    """
    Convert the STAC search results to a pandas DataFrame.

    Parameters
    ----------
    items : ItemSearch
        The item search returned by `search_cmip6()`.

    Returns
    -------
    pd.DataFrame
        The search results represented as a pandas dataframe.

    NOTE: This is just a sample of how to loop through the response. In practice
    you would want to parse other information such as the assets.
    """
    DF_COLUMNS = [
        "title",
        "cmip6:retracted",
        "cmip6:variable_long_name",
        "cmip6:variable_units",
        "cmip6:cf_standard_name",
        "cmip6:activity_id",
        "cmip6:frequency",
        "cmip6:grid_label",
        "cmip6:institution_id",
        "cmip6:mip_era",
        "cmip6:source_id",
        "cmip6:experiment_id",
        "cmip6:table_id",
        "cmip6:variable_id",
        "cmip6:variant_label",
    ]
    df = []
    for page in items.pages():
        df += [
            {
                col.replace("cmip6:", ""): item.properties[col]
                for item in page.items
                for col in DF_COLUMNS
            }
        ]
    return pd.DataFrame(df)


if __name__ == "__main__":
    res = search_cmip6("https://api.stac.ceda.ac.uk", variable_id=["tas", "pr"])
    df = to_dataframe(res)
    print(df)
