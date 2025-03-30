import os
from serpapi import GoogleSearch
from datetime import datetime

## Tool for agent to perform tasks

SERPAPI_KEY= os.getenv("SERPAPI_KEY")

def web_search(query: str, num_results: int = 5) -> str:
    """Fetches search results for a given query using SerpAPI."""
    try:
        search= GoogleSearch({
            "q": query,
            "num": num_results,
            "api_key": SERPAPI_KEY
        })
        results= search.get_dict()

        organic_results= results.get("organic_results", [])
        if not organic_results:
            return "No search results found."
        response= "Here are the top search results:\n"
        for i, result in enumerate(organic_results[:num_results], 1):
            title= result.get("title", "No Title")
            link= result.get("link", "#")
            snippet = result.get("snippet", "No description available.")
            response += f"\n{i}. {title}\n{snippet}\nLink: {link}\n"
        
        return response

    except Exception as e:
        return f"Error fetching search results: {str(e)}"


# Flight search tool
def flight_search(departure_airport: str, arrival_airport: str, outbound_date: str) -> str:
    """
    Futches one-way flight information using SerpApi's Google Flights API.

    Params:
    -departure_airport (str): IATA code of the departure airport (e.g., 'BOM').
    - arrival_airport(str): IATA code of the arrival airport (e.g., 'LKO').
    - outbound_date(str): Outbound flight date in 'YYYY-MM-DD' format.

    Returns:
    - str: Formatted flight search results or an error message.
    """
    try:
        datetime.strptime(outbound_date, '%Y-%m-%d')

        params = {
            "engine": "google_flights",
            "departure_id": departure_airport,
            "arrival_id": arrival_airport,
            "outbound_date": outbound_date,
            "type": "2", 
            "api_key": SERPAPI_KEY
        }

        search= GoogleSearch(params)
        results = search.get_dict()

        best_flights = results.get("best_flights", [])
        if not best_flights:
            return "No flight results found."

        response= "Top one-way flight options:\n"
        for i, flight_option in enumerate(best_flights[:5], 1):
            flights = flight_option.get("flights", [])
            if not flights:
                continue

            flight_details = []
            for flight in flights:
                departure = flight.get("departure_airport", {}).get("id", "Unknown Departure")
                arrival= flight.get("arrival_airport", {}).get("id", "Unknown Arrival")
                departure_time= flight.get("departure_airport", {}).get("time", "Unknown Time")
                arrival_time = flight.get("arrival_airport", {}).get("time", "Unknown Time")
                duration= flight.get("duration", "Duration not available")
                airline= flight.get("airline", "Unknown Airline")
                flight_number = flight.get("flight_number", "Unknown Flight Number")
                travel_class = flight.get("travel_class", "Unknown Class")

                flight_details.append(
                    f"   Flight: {airline} {flight_number}\n"
                    f"   Class: {travel_class}\n"
                    f"   Departure: {departure} at {departure_time}\n"
                    f"   Arrival: {arrival} at {arrival_time}\n"
                    f"   Duration: {duration} minutes\n"
                )

            total_duration = flight_option.get("total_duration", "Total duration not available")
            carbon_emissions = flight_option.get("carbon_emissions", {}).get("this_flight", "N/A")
            price = flight_option.get("price", "Price not available")

            response += (
                f"\nOption {i}:\n"
                f"{''.join(flight_details)}"
                f"   Total Duration: {total_duration} minutes\n"
                f"   Carbon Emissions: {carbon_emissions} grams\n"
                f"   Price: ${price}\n"
            )

        return response

    except ValueError:
        return "Invalid date format. Please use 'YYYY-MM-DD'."
    except Exception as e:
        return f"Error fetching flight information: {str(e)}"
    

def book_flight(city_name: str) -> str:
    return f"You have booked a flight to {city_name}."

def cancel_flight_booking(city_name: str) -> str:
    return f"Your flight to {city_name} has been cancelled."

# Hotel booking tool
def hotel_search(query: str, check_in_date: str, check_out_date: str, adults: int = 1, children: int = 0, currency: str = "USD") -> str:
    """
    Fetches hotel information using SerpApi's Google Hotels API.

    Parameters:
    - query(str): Search query for the hotel location or name (e.g., 'Bali Resorts').
    - check_in_date(str): Check-in date in 'YYYY-MM-DD' format.
    - check_out_date(str): Check-out date in 'YYYY-MM-DD' format.
    - adults(int): Number of adults.
    - children(int): Number of children.
    - currency(str): Currency code for prices (default is 'USD').

    Returns:
    - str: Formatted hotel search results or an error message.
    """
    try:
        datetime.strptime(check_in_date, '%Y-%m-%d')
        datetime.strptime(check_out_date, '%Y-%m-%d')


        params = {
            "engine": "google_hotels",
            "q": query,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": adults,
            "children": children,
            "currency": currency,
            "api_key": SERPAPI_KEY
        }

        search= GoogleSearch(params)
        results = search.get_dict()

        properties = results.get("properties", [])
        if not properties:
            return "No hotel results found."

        response = "Top hotel options:\n"
        for i, property in enumerate(properties[:5], 1):
            name = property.get("name", "Unknown Hotel")
            address= property.get("address", "Address not available")
            rating= property.get("rating", "Rating not available")
            reviews= property.get("reviews", "No reviews")
            price = property.get("rate_per_night", "Price not available")
            amenities = ', '.join(property.get("amenities", [])) or "No amenities listed"

            response += (f"\n{i}. {name}\n"
                         f"   Address: {address}\n"
                         f"   Rating: {rating} ({reviews} reviews)\n"
                         f"   Price per night: {price}\n"
                         f"   Amenities: {amenities}\n")
        return response

    except ValueError:
        return "Invalid date format. Please use 'YYYY-MM-DD'."
    except Exception as e:
        return f"Error fetching hotel information: {str(e)}"

def book_hotels(city_name: str) -> str:
    return f"You have booked a hotel in {city_name}."

def cancel_hotel_booking(hotel_name: str) -> str:
    return f"Your booking at {hotel_name} has been cancelled."

