import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from serpapi import GoogleSearch
from tool_testing import web_search, flight_search, hotel_search, book_hotels, cancel_hotel_booking, book_flight, cancel_flight_booking
from datetime import datetime


#openai_key = os.getenv("OPENAI_API_KEY")

# Created an OpenAI LLM client.
llm = OpenAIChatCompletionClient(model="gpt-4o")


# Defined date and time for the agents.
today = datetime.now()
date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."


# Here I have Define the tourism expert agent for travel related quries.(Using Serp API for web search)
travel_guide_expert = AssistantAgent(
    "travel_guide_expert",
    model_client=llm,
    handoffs=["user", "hotel_expert", "travel_bookings_expert"],
    tools=[web_search],
    system_message="""You are a travel planner agent and {date_context}, You know alot about different travel destinations across India including different places, cities, etc. 
    You can help the user with travel planning and provide information of different travel destinations like places to visit, things to do, etc.
    You have the ability to search the web for information about places, cities, things to do, etc using web_search tool.
    The hotel_expert is in charge of searching, booking/cancellation for hotel.
    The travel_bookings_expert is in charge of searching, booking/cancellation for travel tickets.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Always ask the user for the travel destination and how you can help them.
    And handoff to the user for confirmation before proceeding with the travel planning.
    Use TERMINATE when the travel planning is complete.""",
)

# Defined the Flight Ticket Booking Agent for Travel related quries (Using Serp API to get Real Time Flight Details)
travel_bookings_expert = AssistantAgent(
    "travel_bookings_expert",
    model_client=llm,
    handoffs=["user", "travel_guide_expert", "hotel_expert"],
    tools=[flight_search, book_flight, cancel_flight_booking],
    system_message=f"""You are a travel booking agent and {date_context} You can help the user with searching, booking, or cancel bookings of the flight tickets all across India.
    You have the ability to search flight using book_flight tool.
    You can book or cancel the booking of the ticket using book_flight, cancel_flight_booking
    You can handoff to hotel_expert agent for hotel booking.
    You can handoff to travel_guide_expert agent for more information about the travel destination.
    Always ask the user for the travel destination and travel dates before providing any information.
    And handoff to the user for confirmation before proceeding with the flight booking.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""",
)


# Here Defined the Hotel Booking Expert for hotel releated Quries (Using Serp API to get Real Time Hotel Details)
hotel_expert = AssistantAgent(
    "hotel_expert",
    model_client=llm,
    handoffs=["user", "travel_guide_expert", "travel_bookings_expert"],
    tools=[hotel_search, book_hotels, cancel_hotel_booking],
    system_message="""You are a hotel booking agent and {date_context}. You can help the user with searching, booking, or cancel bookings of the hotels all across India.
    You have the ability to search for information about hotels using hotel_search tool and book or cancel the booking of the hotel using book_hotels and cancel_hotel_booking tools.
    You can handoff to travel_guide_expert agent for more information about the travel destination.
    You can handoff to travel_bookings_expert agent for travel ticket booking.
    Always ask the user for the information required for hotel search like check-in and check-out dates, number of adults and children, etc. Current year is 2025
    And handoff to the user for confirmation before proceeding with the hotel booking.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""",
)


# Use Termination to exit the cb
termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")

# Using Swarm to handover task to differnet agents
team = Swarm([travel_guide_expert, hotel_expert, travel_bookings_expert], termination_condition=termination)

# Defined the task blow
task = "Help the user with travel planning." 


# Aysichrously running all agents chat system
async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]



async def main():
    await run_team_stream()
    await llm.close()

if __name__ == "__main__":
    asyncio.run(main())


