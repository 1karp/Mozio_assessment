import requests
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

API_BASE_URL = "https://api-testing.mozio.com/v2"
API_KEY = os.getenv("API_KEY")
headers = {"API-KEY": API_KEY, "Content-Type": "application/json"}

# Rest of your code remains the same...


session = requests.Session()
session.headers.update(headers)


def _make_request(
    method: str, url: str, data: dict[str, [str | int | list[str]]] = None
) -> dict:
    """
    Send an API request to the specified URL with the given method and data.

    Args:
        method (str): The HTTP method for the request (e.g., 'GET', 'POST', 'DELETE', etc.).
        url (str): The URL of the API endpoint.
        data (dict): The JSON data to be sent with the request (default: None).

    Returns:
        dict: The JSON response data as a dictionary.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.
    """
    response = session.request(method, url, json=data)
    response.raise_for_status()
    return response.json()


def search(
    start_address: str,
    end_address: str,
    mode: str,
    pickup_datetime: str,
    num_passengers: int,
    currency: str,
    campaign: str,
) -> dict:
    url = f"{API_BASE_URL}/search/"
    data = {
        "start_address": start_address,
        "end_address": end_address,
        "mode": mode,
        "pickup_datetime": pickup_datetime,
        "num_passengers": num_passengers,
        "currency": currency,
        "campaign": campaign,
    }
    return _make_request("POST", url, data)


def poll_search(
    search_id: str, max_polls: int = 10, poll_interval: int = 1
) -> list[dict]:
    url = f"{API_BASE_URL}/search/{search_id}/poll/"
    poll_responses = []

    for _ in range(max_polls):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        poll_data = response.json()

        poll_responses.append(poll_data)

        if not poll_data["more_coming"]:
            break

        time.sleep(poll_interval)

    return poll_responses


def make_reservation(search_id: str, result_id: str) -> dict:
    url = f"{API_BASE_URL}/reservations/"
    data = {
        "search_id": search_id,
        "result_id": result_id,
        "email": "tester_artem@gmail.com",
        "country_code_name": "US",
        "phone_number": "8776665524",
        "first_name": "Artemtest",
        "last_name": "Karpovtest",
        "airline": "LH",
        "flight_number": "161",
        "customer_special_instructions": "My doorbell is broken, please yell",
    }

    return _make_request("POST", url, data)


def poll_reservation_result(
    search_id: str, max_polls: int = 20, poll_interval: int = 1
) -> dict:
    url = f"{API_BASE_URL}/reservations/{search_id}/poll/"

    while True:
        response_json = _make_request("GET", url)

        if response_json["status"] == "completed":
            return response_json

        time.sleep(poll_interval)


def cancel_reservation(confirmation_number: str) -> bool:
    url = f"{API_BASE_URL}/reservations/{confirmation_number}"
    response = _make_request("DELETE", url)
    return response["cancelled"]
