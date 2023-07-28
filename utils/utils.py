def get_provider_results(data, provider_name):
    for response in data:
        if "results" in response:
            for result in response["results"]:
                if result["steps"][0]["details"]["provider_name"] == provider_name:
                    yield result


def find_lowest_price_id(data, provider_name="Dummy External Provider"):
    try:
        lowest_price = float("inf")
        lowest_price_id = None

        for result in get_provider_results(data, provider_name):
            value = float(result["total_price"]["total_price"]["value"])
            if value < lowest_price:
                lowest_price = value
                lowest_price_id = result["result_id"]

        return lowest_price_id

    except (KeyError, TypeError, ValueError) as e:
        print(f"Error occurred during finding of the lowest price: {e}")
        return None
