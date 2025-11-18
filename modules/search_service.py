from .db_manager import DBManager
from datetime import datetime, date
import re


class SearchService:
    """Service class for handling search operations"""
    
    def __init__(self):
        self.db_manager = DBManager("db")
    
    def parse_date(self, date_str):
        """Parse date string in DD/MM/YYYY or YYYY-MM-DD format"""
        try:
            # Try DD/MM/YYYY format
            return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        except ValueError:
            try:
                # Try YYYY-MM-DD format
                return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
            except ValueError:
                return None
    
    def validate_date_format(self, date_str):
        """Validate date format"""
        if not date_str or not date_str.strip():
            return False
        
        # Check DD/MM/YYYY format
        pattern1 = r'^\d{2}/\d{2}/\d{4}$'
        # Check YYYY-MM-DD format
        pattern2 = r'^\d{4}-\d{2}-\d{2}$'
        
        return bool(re.match(pattern1, date_str.strip()) or re.match(pattern2, date_str.strip()))
    
    def validate_search_dates(self, checkin_str, checkout_str):
        """
        Validate search dates
        
        Returns:
            Tuple (is_valid: bool, error_message: str)
        """
        # If both fields are empty, no error
        if not checkin_str and not checkout_str:
            return True, ""
        
        # Validate check-in date
        if checkin_str:
            if not self.validate_date_format(checkin_str):
                return False, "Check-in date must be in DD/MM/YYYY format"
            
            checkin_date = self.parse_date(checkin_str)
            if checkin_date is None:
                return False, "Invalid check-in date format"
            
            # Check if check-in date is not in the past
            today = date.today()
            if checkin_date < today:
                return False, "Check-in date cannot be in the past"
        
        # Validate check-out date
        if checkout_str:
            if not self.validate_date_format(checkout_str):
                return False, "Check-out date must be in DD/MM/YYYY format"
            
            checkout_date = self.parse_date(checkout_str)
            if checkout_date is None:
                return False, "Invalid check-out date format"
        
        # Validate check-out is after check-in
        if checkin_str and checkout_str:
            checkin_date = self.parse_date(checkin_str)
            checkout_date = self.parse_date(checkout_str)
            
            if checkin_date and checkout_date:
                if checkout_date <= checkin_date:
                    return False, "Check-out date must be after check-in date"
        
        return True, ""
    
    def get_all_room_types(self):
        """Get all room types from database"""
        return self.db_manager.get_all_room_types()
    
    def get_room_type_by_name(self, type_name):
        """Get room type by name"""
        room_types = self.db_manager.get_all_room_types()
        for rt in room_types:
            if rt["typeName"] == type_name:
                return rt
        return None
    
    def get_room_type_id_by_name(self, type_name):
        """Get room type ID by type name"""
        room_type = self.get_room_type_by_name(type_name)
        return room_type["typeID"] if room_type else None
    
    def find_available_rooms(self, check_in, check_out, room_type_name=None):
        """
        Find available rooms for given dates and optional room type
        
        Args:
            check_in: check-in date (date object)
            check_out: check-out date (date object)
            room_type_name: room type name (string), None for all types
            
        Returns:
            List of available rooms with room type information
        """
        # Get room type ID if specified
        type_id = None
        if room_type_name and room_type_name != "All Types":
            type_id = self.get_room_type_id_by_name(room_type_name)
        
        # Find available rooms from database
        available_rooms = self.db_manager.find_available_rooms_by_date(
            check_in, check_out, type_id
        )
        
        # Enrich rooms with room type information
        room_types = self.db_manager.get_all_room_types()
        room_type_dict = {rt["typeID"]: rt for rt in room_types}
        
        enriched_rooms = []
        for room in available_rooms:
            room_with_type = room.copy()
            room_with_type["roomType"] = room_type_dict.get(room["typeID"], {})
            enriched_rooms.append(room_with_type)
        
        return enriched_rooms
    
    def filter_rooms_by_price(self, rooms, min_price=0, max_price=999999999):
        """
        Filter rooms by price range
        
        Args:
            rooms: list of rooms (with roomType info)
            min_price: minimum price
            max_price: maximum price
            
        Returns:
            Filtered list of rooms
        """
        filtered = []
        for room in rooms:
            room_type = room.get("roomType", {})
            price = room_type.get("price", 0)
            if min_price <= price <= max_price:
                filtered.append(room)
        return filtered
    
    def filter_rooms_by_type(self, rooms, room_type_name):
        """
        Filter rooms by type name
        
        Args:
            rooms: list of rooms (with roomType info)
            room_type_name: room type name (string)
            
        Returns:
            Filtered list of rooms
        """
        if room_type_name == "All Types":
            return rooms
        
        filtered = []
        for room in rooms:
            room_type = room.get("roomType", {})
            if room_type.get("typeName") == room_type_name:
                filtered.append(room)
        return filtered
    
    def apply_filters(self, rooms, min_price=0, max_price=999999999, room_type_name="All Types"):
        """
        Apply multiple filters to rooms
        
        Args:
            rooms: list of rooms (with roomType info)
            min_price: minimum price
            max_price: maximum price
            room_type_name: room type name (string)
            
        Returns:
            Filtered list of rooms
        """
        # Apply price filter
        filtered = self.filter_rooms_by_price(rooms, min_price, max_price)
        
        # Apply type filter
        filtered = self.filter_rooms_by_type(filtered, room_type_name)
        
        return filtered
