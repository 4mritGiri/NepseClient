"""
Dummy ID management for NEPSE API requests.

This module manages the generation and caching of dummy IDs used in
POST request payloads, ensuring they stay synchronized with market status.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Callable, Optional


logger = logging.getLogger(__name__)


class _DummyIDManagerBase:
    """
    Base class for dummy ID managers.

    Manages dummy IDs that are required for certain NEPSE API requests.
    The dummy ID changes based on market status and date.

    Args:
       market_status_function: Function to get market status
       date_function: Function to get current datetime (default: datetime.now)
    """

    def __init__(
        self,
        market_status_function: Optional[Callable] = None,
        date_function: Callable = datetime.now,
    ):
        """Initialize dummy ID manager."""
        self.data: Optional[dict] = None
        self.dummy_id: Optional[int] = None
        self.date_stamp: Optional[datetime] = None

        self.setDateFunction(date_function)
        self.setMarketStatusFunction(
            market_status_function or (lambda: {"id": 0, "asOf": datetime.now().isoformat()})
        )

    def setDateFunction(self, func: Callable) -> None:
        """
        Set function to get current date/time.

        Args:
           func: Callable that returns datetime
        """
        self.date_function = func

    def setMarketStatusFunction(self, func: Callable) -> None:
        """
        Set function to get market status.

        Args:
           func: Callable that returns market status dict
        """
        self.market_status_function = func
        self.data = None  # Reset data when function changes

    def convertToDateTime(self, date_time_str: str) -> datetime:
        """
        Convert date string to datetime object.

        Handles various datetime formats and microsecond precision issues.

        Args:
           date_time_str: Date/time string from API

        Returns:
           Parsed datetime object
        """
        # Handle microseconds properly (limit to 6 decimal places)
        if "." in date_time_str:
            pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d+)?"
            match = re.match(pattern, date_time_str)

            if match:
                main_part = match.group(1)
                decimal_part = match.group(2)

                if decimal_part:
                    # Limit to 6 decimal places (microseconds)
                    decimal_part = decimal_part[:7]  # . + 6 digits
                    formatted_str = main_part + decimal_part
                    try:
                        return datetime.strptime(formatted_str, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        logger.warning("ValueError occured..")

                # Fall back to second-level parsing
                return datetime.strptime(main_part, "%Y-%m-%dT%H:%M:%S")

        # Default parsing without microseconds
        return datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S")

    def __repr__(self) -> str:
        """Return the string representation of the dummy ID manager."""
        if self.dummy_id is None:
            return "Dummy ID Manager: Not Initialized"

        date_str = self.date_stamp.strftime("%Y-%m-%d %H:%M:%S") if self.date_stamp else "N/A"
        return f"Dummy ID Manager (ID: {self.dummy_id}, Date: {date_str})"


class DummyIDManager(_DummyIDManagerBase):
    """
    Synchronous dummy ID manager.

    Manages dummy IDs for synchronous NEPSE client, automatically
    updating when the date changes or market status is updated.
    """

    def __init__(
        self,
        market_status_function: Optional[Callable] = None,
        date_function: Callable = datetime.now,
    ):
        """Initialize synchronous dummy ID manager."""
        super().__init__(market_status_function, date_function)

    def populateData(self, force: bool = False) -> None:
        """
        Fetch and populate dummy ID data.

        Args:
           force: Force refresh even if data exists
        """
        today = self.date_function()

        # Initialize data if not present or forced
        if self.data is None or force:
            logger.debug("Initializing dummy ID data")
            self.data = self.market_status_function()
            self.dummy_id = self.data["id"]
            self.date_stamp = today
            logger.info(f"Dummy ID initialized: {self.dummy_id}")
            return

        # Check if date has changed
        if self.date_stamp is None or self.date_stamp.date() < today.date():
            # if self.date_stamp.date() < today.date():
            logger.debug("Date changed, updating dummy ID")
            new_data = self.market_status_function()
            new_converted_date = self.convertToDateTime(new_data["asOf"])

            # Check if NEPSE date matches current date
            if new_converted_date.date() == today.date():
                self.data = new_data
                self.dummy_id = self.data["id"]
                self.date_stamp = new_converted_date
                logger.info(f"Dummy ID updated: {self.dummy_id}")
            else:
                # NEPSE is closed (holiday/weekend)
                # Set date stamp to today to avoid repeated checks
                self.data = new_data
                self.dummy_id = self.data["id"]
                self.date_stamp = today
                logger.debug("Market closed, using previous dummy ID")

    def getDummyID(self) -> int:
        """
        Get current dummy ID, updating if necessary.

        Returns:
           Current dummy ID
        """
        self.populateData()
        assert self.dummy_id is not None
        return self.dummy_id


class AsyncDummyIDManager(_DummyIDManagerBase):
    """
    Asynchronous dummy ID manager.

    Manages dummy IDs for asynchronous NEPSE client, with support
    for concurrent operations and proper async synchronization.
    """

    def __init__(
        self,
        market_status_function: Optional[Callable] = None,
        date_function: Callable = datetime.now,
    ):
        """Initialize asynchronous dummy ID manager."""
        super().__init__(market_status_function, date_function)

        # Synchronization events for concurrent operations
        self.update_started = asyncio.Event()
        self.update_completed = asyncio.Event()

    async def populateData(self, force: bool = False) -> None:
        """
        Fetch and populate dummy ID data asynchronously.

        Ensures only one update operation happens at a time, even with
        concurrent requests.

        Args:
           force: Force refresh even if data exists
        """
        today = self.date_function()

        # Initialize data if not present or forced
        if self.data is None or force:
            # Check if another coroutine is already updating
            if not self.update_started.is_set():
                self.update_started.set()
                self.update_completed.clear()

                try:
                    logger.debug("Initializing dummy ID data")
                    self.data = await self.market_status_function()
                    self.dummy_id = self.data["id"]
                    self.date_stamp = today
                    logger.info(f"Dummy ID initialized: {self.dummy_id}")

                finally:
                    self.update_completed.set()
                    self.update_started.clear()
            else:
                # Wait for ongoing update to complete
                await self.update_completed.wait()
            return

        # Check if date has changed
        if self.date_stamp is None or self.date_stamp.date() < today.date():
            # if self.date_stamp.date() < today.date():
            # Check if another coroutine is already updating
            if self.update_started.is_set():
                # Wait for ongoing update
                await self.update_completed.wait()
            else:
                # Start update
                self.update_started.set()
                self.update_completed.clear()

                try:
                    logger.debug("Date changed, updating dummy ID")
                    new_data = await self.market_status_function()
                    new_converted_date = self.convertToDateTime(new_data["asOf"])

                    # Check if NEPSE date matches current date
                    if new_converted_date.date() == today.date():
                        self.data = new_data
                        self.dummy_id = self.data["id"]
                        self.date_stamp = new_converted_date
                        logger.info(f"Dummy ID updated: {self.dummy_id}")
                    else:
                        # NEPSE is closed (holiday/weekend)
                        self.data = new_data
                        self.dummy_id = self.data["id"]
                        self.date_stamp = today
                        logger.debug("Market closed, using previous dummy ID")

                finally:
                    self.update_completed.set()
                    self.update_started.clear()

    async def getDummyID(self) -> int:
        """
        Get current dummy ID, updating if necessary.

        Returns:
           Current dummy ID
        """
        await self.populateData()
        assert self.dummy_id is not None
        return self.dummy_id


__all__ = [
    "DummyIDManager",
    "AsyncDummyIDManager",
]
