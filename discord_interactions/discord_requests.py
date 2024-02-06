import json
import aiohttp


class ScheduledEvents:
    """Class connected to discord endpoint via http to communicate with it.
    """

    GUILD_ONLY = 2
    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3

    # load_dotenv()
    # TOKEN:str = os.getenv("TOKEN")
    TOKEN: str = "MTE3NjgzODkzMTgxNjM5MDcyNw.Gz2bEs.c5m9RvysF6Meu8fbQta8uVU2JiBHQp84MNONIo"
    BOT_AUTH_HEADER: str = ""
    API_URL: str = "https://discord.com/api/v10"

    AUTH_HEADERS: dict = {
        "Authorization": f"Bot {TOKEN}",
        "User-Agent": f"DiscordBot ({BOT_AUTH_HEADER}) Python/3.9 aiohttp/3.7.4",
        "Content-Type": "application/json"
    }

    @staticmethod
    async def list_guild_events(guild_id: int) -> list:
        """Returns a list of upcoming events for the supplied guild ID
        Format of return is a list of one dictionary per event containing information.

        Args:
            guild_id (int): Guild id in the endpoint

        Returns:
            list: Events as objects
        """

        ENDPOINT_URL = f"{ScheduledEvents.API_URL}/guilds/{guild_id}/scheduled-events"

        async with aiohttp.ClientSession(headers=ScheduledEvents.AUTH_HEADERS) as session:
            try:
                async with session.get(ENDPOINT_URL) as response:
                    response.raise_for_status()
                    assert response.status == 200
                    response_list = json.loads(await response.read())
                    print(f"Get success: to {ENDPOINT_URL}")
            except Exception as e:
                print(f"Get error: to {ENDPOINT_URL} as {e}")
            finally:
                await session.close()
        return response_list

    @staticmethod
    async def find_guild_event(target_name: str, guild_id: int) -> str:
        """Returns id of guild event by given event namme.

        Args:
            target_name (str): Name of the event to find
            guild_id (int): In which guild to search in

        Raises:
            ValueError: When not found withing guild

        Returns:
            str: id of the found event
        """
        all = await ScheduledEvents.list_guild_events(guild_id)
        for event in all:
            if event["name"] == target_name:
                return event["id"]
            if target_name in event["name"]:
                return event["id"]
        raise ValueError(
            f"Event with {target_name=} cannot be found in {guild_id=}")

    @staticmethod
    async def create_guild_event(guild_id: int, event_name: str,
                                 event_description: str,  event_start_time: str, event_end_time: str,
                                 event_metadata: dict, channel_id: int = None):
        """Creates a guild event using the supplied arguments.
        The expected event_metadata format is event_metadata={"location": "YOUR_LOCATION_NAME"}
        The required time format is %Y-%m-%dT%H:%M:%S aka ISO8601

        Args:
            guild_id (str): Guild id in endpoint
            event_name (str): Name of event
            event_description (str): Description of event
            event_start_time (str): Start timestamp
            event_end_time (str): End timestamp 
            event_metadata (dict): External location data
            channel_id (int, optional): Id of voice channel. Defaults to None.
        Raises:
            ValueError: Cannot have both (event_metadata) and (channel_id) 
            at the same time.
        """
        if channel_id and event_metadata:
            raise ValueError(
                f"If event_metadata is set, channel_id must be set to None. And vice versa.")

        ENDPOINT_URL = f"{ScheduledEvents.API_URL}/guilds/{guild_id}/scheduled-events"
        entity_type = ScheduledEvents.EXTERNAL if channel_id is None else ScheduledEvents.VOICE

        event_data = json.dumps({
            "name": event_name,
            "privacy_level": ScheduledEvents.GUILD_ONLY,
            "scheduled_start_time": event_start_time,
            "scheduled_end_time": event_end_time,
            "description": event_description,
            "channel_id": channel_id,
            "entity_metadata": event_metadata,
            "entity_type": entity_type
        })

        async with aiohttp.ClientSession(headers=ScheduledEvents.AUTH_HEADERS) as session:
            try:
                async with session.post(ENDPOINT_URL, data=event_data) as response:
                    response.raise_for_status()
                    assert response.status == 200
                    print(f"Post success: to {ENDPOINT_URL}")
            except Exception as e:
                print(f"Post error: to {ENDPOINT_URL} as {e}")
                await session.close()
                return

            await session.close()
            return response

    @staticmethod
    async def modify_guild_event(event: int, guild_id: int, event_name: str,
                                 event_description: str,  event_start_time: str, event_end_time: str,
                                 event_metadata: dict, channel_id: int = None):
        """Creates a guild event using the supplied arguments.
        The expected event_metadata format is event_metadata={"location": "YOUR_LOCATION_NAME"}
        The required time format is %Y-%m-%dT%H:%M:%S aka ISO8601

        Args:
            guild_id (str): Guild id in endpoint
            event_name (str): Name of event
            event_description (str): Description of event
            event_start_time (str): Start timestamp
            event_end_time (str): End timestamp 
            event_metadata (dict): External location data
            channel_id (int, optional): Id of voice channel. Defaults to None.
        Raises:
            ValueError: Cannot have both (event_metadata) and (channel_id) 
            at the same time.
        """
        if channel_id and event_metadata:
            raise ValueError(
                f"If event_metadata is set, channel_id must be set to None. And vice versa.")

        ENDPOINT_URL = f"{ScheduledEvents.API_URL}/guilds/{guild_id}/scheduled-events/{event}"
        entity_type = ScheduledEvents.EXTERNAL if channel_id is None else ScheduledEvents.VOICE

        event_data = json.dumps({
            "name": event_name,
            "privacy_level": ScheduledEvents.GUILD_ONLY,
            "scheduled_start_time": event_start_time,
            "scheduled_end_time": event_end_time,
            "description": event_description,
            "channel_id": channel_id,
            "entity_metadata": event_metadata,
            "entity_type": entity_type
        })

        async with aiohttp.ClientSession(headers=ScheduledEvents.AUTH_HEADERS) as session:
            try:
                async with session.patch(ENDPOINT_URL, data=event_data) as response:
                    response.raise_for_status()
                    assert response.status == 200
                    print(f"Patch success: to {ENDPOINT_URL}")
            except Exception as e:
                print(f"Patch error: to {ENDPOINT_URL} as {e}")
                await session.close()
                return

            await session.close()
            return response

    @staticmethod
    async def delete_guild_event(guild_id: int, event_id: str):
        ENDPOINT_URL = f"{ScheduledEvents.API_URL}/guilds/{guild_id}/scheduled-events/{event_id}"

        async with aiohttp.ClientSession(headers=ScheduledEvents.AUTH_HEADERS) as session:
            try:
                async with session.delete(ENDPOINT_URL) as response:
                    response.raise_for_status()
                    assert response.status == 204
                    print(f"Delete success: to {ENDPOINT_URL}")
            except Exception as e:
                print(f"Delete error: to {ENDPOINT_URL} as {e}")
                await session.close()
                return

            await session.close()
            return response
