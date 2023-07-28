import requests


from api.mozio_api import (
    search,
    poll_search,
    poll_reservation_result,
    make_reservation,
    cancel_reservation,
)
from utils.utils import find_lowest_price_id
from utils.logging import logging

BOOKING_DATA = {
    "start_address": "44 Tehama Street, San Francisco, CA, USA",
    "end_address": "SFO",
    "mode": "one_way",
    "pickup_datetime": "2023-12-01 15:30:10",
    "num_passengers": 2,
    "currency": "USD",
    "campaign": "Artem Karpov",
}


def perform_search():
    """
    Perform a search and poll the results to find the lowest price.

    Returns:
        tuple: A tuple containing the search ID and the lowest price result ID.
              (search_id: str, lowest_price_id: str)
    """
    try:
        logging.info("Performing Search...")
        search_response = search(**BOOKING_DATA)

        if not search_response["search_id"]:
            logging.error("Search did not return any results.")
            return None

        search_id = search_response["search_id"]
        logging.info(f"Search completed, search_id={search_id}")

        logging.info("Polling search...")
        poll_responses = poll_search(search_id)

    except requests.exceptions.RequestException as err:
        logging.error(f"An error occurred during Search API request: {err}")
        return None

    except KeyError as err:
        logging.error(f"KeyError during Search: {err}")
        return None

    logging.info("Getting lowest price...")
    lowest_price_id = find_lowest_price_id(poll_responses)
    logging.info(f"Lowest_price_id={lowest_price_id}")

    return search_id, lowest_price_id


def perform_reservation(search_id, lowest_price_id):
    """
    Perform a reservation using the provided search ID and lowest price result ID.

    Args:
        search_id (str): The search ID returned from the search API.
        lowest_price_id (str): The result ID with the lowest price.

    Returns:
        str: The confirmation number of the reservation if successful; otherwise, None.
    """
    try:
        logging.info("Making a reservation...")
        make_reservation(search_id, lowest_price_id)

        logging.info("Waiting for reservation confirmation...")
        poll_reservations = poll_reservation_result(search_id)
        confirmation_number = poll_reservations["reservations"][0]["id"]

        logging.info(f"Reservation confirmation number: {confirmation_number}")
        return confirmation_number

    except requests.exceptions.RequestException as err:
        logging.error(f"An error occurred during Reservation API request: {err}")
        return None

    except KeyError as err:
        logging.error(f"KeyError during Reservation: {err}")
        return None


def reservation_tests():
    logging.info("Starting the reservation tests...")

    search_id, lowest_price_id = perform_search()

    if search_id and lowest_price_id:
        confirmation_number = perform_reservation(search_id, lowest_price_id)
        logging.info(f"Confirmation number is {confirmation_number}")

        if confirmation_number:
            cancel_status = cancel_reservation(confirmation_number)

            if cancel_status:
                logging.info(
                    f"Reservation confirmed with confirmation number: {confirmation_number}"
                )
                logging.info("Reservation canceled")
                print(
                    "Reservation confirmed with confirmation number:",
                    confirmation_number,
                )
            else:
                logging.error("Reservation cancellation failed.")
                print("Reservation cancellation failed.")
        else:
            logging.error("Reservation booking failed.")
            print("Reservation booking failed.")
    else:
        logging.error("Reservation search failed.")
        print("Reservation search failed.")


if __name__ == "__main__":
    reservation_tests()
