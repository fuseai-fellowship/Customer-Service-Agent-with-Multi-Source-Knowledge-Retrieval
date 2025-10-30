from langchain_core.tools import tool
from typing import Optional
import os, requests

@tool
def menu_tool(
    search: Optional[str] = None,
    type: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
) -> dict:
    """
    Retrieves restaurant menu items based on the provided criteria.

    Args:
        search (str | None): Dish name or keyword to search for.
        type (str | None): "veg" or "nonveg" to filter dish type.
        price_min (float | None): Minimum price filter.
        price_max (float | None): Maximum price filter.

    Returns:
        dict: Dictionary containing matching menu items
    """
    base_url = os.getenv("BASE_URL")
    items_url = base_url + "/items"
    params = {
        "search": search,
        "type": type,
        "price_min": price_min,
        "price_max": price_max
    }

    try:
        response = requests.get(items_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling backend: {e}")
        return {"error": str(e)}