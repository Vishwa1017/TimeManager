import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.tools import tool
from langchain_google_community import CalendarToolkit

from utils.logger import get_logger


logger = get_logger(__name__)

TIMEZONE = "America/Toronto"
PRIMARY_CALENDAR_ID = "viswa3388@gmail.com"

toolkit = CalendarToolkit()
raw_tools = toolkit.get_tools()

raw = {calendar_tool.name: calendar_tool for calendar_tool in raw_tools}

create_raw = raw["create_calendar_event"]
search_raw = raw["search_events"]
update_raw = raw["update_calendar_event"]
move_raw = raw["move_calendar_event"]
delete_raw = raw["delete_calendar_event"]
calendar_info_raw = raw["get_calendars_info"]


def clean_datetime(datetime_value: str) -> str:
    """
    Convert ISO-style datetime strings into the format expected
    by the Google Calendar tools.
    """

    return (
        datetime_value
        .replace("T", " ")
        .replace("-04:00", "")
        .replace("-05:00", "")
        .replace("+00:00", "")
        .strip()
    )


@tool
def get_current_datetime_safe() -> str:
    """Get the current date and time in America/Toronto."""

    now = datetime.now(ZoneInfo(TIMEZONE))
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

    logger.info(
        "Retrieved current datetime timezone=%s datetime=%s",
        TIMEZONE,
        formatted_datetime,
    )

    return formatted_datetime


@tool
def get_calendars_info_safe() -> str:
    """Get available Google Calendar information."""

    logger.info("Retrieving Google Calendar information")

    try:
        result = calendar_info_raw.invoke({})

        logger.info(
            "Successfully retrieved Google Calendar information"
        )

        return result

    except Exception:
        logger.exception(
            "Failed to retrieve Google Calendar information"
        )
        raise


@tool
def search_calendar_events(
    min_datetime: str,
    max_datetime: str,
    max_results: int = 20,
) -> str:
    """
    Search calendar events between min_datetime and max_datetime.

    Expected datetime format:
    YYYY-MM-DD HH:MM:SS
    """

    cleaned_min_datetime = clean_datetime(min_datetime)
    cleaned_max_datetime = clean_datetime(max_datetime)

    payload = {
        "calendars_info": json.dumps(
            [
                {
                    "id": PRIMARY_CALENDAR_ID,
                    "summary": PRIMARY_CALENDAR_ID,
                    "timeZone": TIMEZONE,
                }
            ]
        ),
        "min_datetime": cleaned_min_datetime,
        "max_datetime": cleaned_max_datetime,
        "max_results": max_results,
    }

    logger.info(
        "Searching calendar events start=%s end=%s max_results=%s",
        cleaned_min_datetime,
        cleaned_max_datetime,
        max_results,
    )

    logger.debug(
        "Calendar search payload=%s",
        payload,
    )

    try:
        result = search_raw.invoke(payload)

        logger.info(
            "Calendar search completed successfully start=%s end=%s",
            cleaned_min_datetime,
            cleaned_max_datetime,
        )

        return result

    except Exception:
        logger.exception(
            "Calendar search failed start=%s end=%s",
            cleaned_min_datetime,
            cleaned_max_datetime,
        )
        raise


@tool
def create_calendar_event_safe(
    title: str,
    start_datetime: str,
    end_datetime: str,
) -> str:
    """
    Create a calendar event.

    Expected datetime format:
    YYYY-MM-DD HH:MM:SS
    """

    cleaned_start_datetime = clean_datetime(start_datetime)
    cleaned_end_datetime = clean_datetime(end_datetime)

    payload = {
        "calendar_id": "primary",
        "summary": title,
        "start_datetime": cleaned_start_datetime,
        "end_datetime": cleaned_end_datetime,
        "timezone": TIMEZONE,
    }

    logger.info(
        "Creating calendar event title=%s start=%s end=%s",
        title,
        cleaned_start_datetime,
        cleaned_end_datetime,
    )

    logger.debug(
        "Calendar create payload=%s",
        payload,
    )

    maximum_attempts = 3

    for attempt in range(1, maximum_attempts + 1):
        try:
            result = create_raw.invoke(payload)

            logger.info(
                "Calendar event created successfully title=%s attempt=%s",
                title,
                attempt,
            )

            return result

        except Exception as error:
            if attempt < maximum_attempts:
                logger.warning(
                    "Calendar event creation failed title=%s "
                    "attempt=%s/%s error=%s",
                    title,
                    attempt,
                    maximum_attempts,
                    error,
                )

                time.sleep(2)

            else:
                logger.exception(
                    "Calendar event creation failed after %s attempts "
                    "title=%s",
                    maximum_attempts,
                    title,
                )
                raise

    raise RuntimeError(
        "Calendar event creation ended unexpectedly."
    )


@tool
def update_calendar_event_safe(
    event_id: str,
    title: str,
    start_datetime: str,
    end_datetime: str,
) -> str:
    """
    Update an existing calendar event.

    Requires an event_id. Search for the event first when the
    event_id is unknown.
    """

    cleaned_start_datetime = clean_datetime(start_datetime)
    cleaned_end_datetime = clean_datetime(end_datetime)

    payload = {
        "calendar_id": "primary",
        "event_id": event_id,
        "summary": title,
        "start_datetime": cleaned_start_datetime,
        "end_datetime": cleaned_end_datetime,
        "timezone": TIMEZONE,
    }

    logger.info(
        "Updating calendar event event_id=%s title=%s start=%s end=%s",
        event_id,
        title,
        cleaned_start_datetime,
        cleaned_end_datetime,
    )

    logger.debug(
        "Calendar update payload=%s",
        payload,
    )

    try:
        result = update_raw.invoke(payload)

        logger.info(
            "Calendar event updated successfully event_id=%s title=%s",
            event_id,
            title,
        )

        return result

    except Exception as error:
        error_message = str(error).upper()

        is_ssl_error = (
            "SSL" in error_message
            or "RECORD_LAYER_FAILURE" in error_message
        )

        if not is_ssl_error:
            logger.exception(
                "Calendar event update failed event_id=%s title=%s",
                event_id,
                title,
            )
            raise

        logger.warning(
            "SSL error while updating calendar event. "
            "Retrying once event_id=%s error=%s",
            event_id,
            error,
        )

    try:
        result = update_raw.invoke(payload)

        logger.info(
            "Calendar event updated successfully after SSL retry "
            "event_id=%s title=%s",
            event_id,
            title,
        )

        return result

    except Exception:
        logger.exception(
            "Calendar event update failed after SSL retry "
            "event_id=%s title=%s",
            event_id,
            title,
        )
        raise


@tool
def move_calendar_event_safe(
    event_id: str,
    destination_calendar_id: str = "primary",
) -> str:
    """
    Move an event to another calendar.

    The destination_calendar_id will normally remain primary.
    """

    payload = {
        "calendar_id": "primary",
        "event_id": event_id,
        "destination_calendar_id": destination_calendar_id,
    }

    logger.info(
        "Moving calendar event event_id=%s destination=%s",
        event_id,
        destination_calendar_id,
    )

    logger.debug(
        "Calendar move payload=%s",
        payload,
    )

    try:
        result = move_raw.invoke(payload)

        logger.info(
            "Calendar event moved successfully event_id=%s destination=%s",
            event_id,
            destination_calendar_id,
        )

        return result

    except Exception:
        logger.exception(
            "Failed to move calendar event event_id=%s destination=%s",
            event_id,
            destination_calendar_id,
        )
        raise


@tool
def delete_calendar_event_safe(event_id: str) -> str:
    """
    Delete a calendar event.

    Requires an event_id. Search for the event first when the
    event_id is unknown.
    """

    payload = {
        "calendar_id": "primary",
        "event_id": event_id,
    }

    logger.info(
        "Deleting calendar event event_id=%s",
        event_id,
    )

    logger.debug(
        "Calendar delete payload=%s",
        payload,
    )

    try:
        result = delete_raw.invoke(payload)

        logger.info(
            "Calendar event deleted successfully event_id=%s",
            event_id,
        )

        return result

    except Exception:
        logger.exception(
            "Failed to delete calendar event event_id=%s",
            event_id,
        )
        raise