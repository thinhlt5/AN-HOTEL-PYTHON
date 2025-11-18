from .db_manager import DBManager
import os
import shutil
from datetime import datetime

class RoomService:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager("db")
        self.images_folder = "assets/images"
        # Create images folder if it doesn't exist (using absolute path)
        abs_images_folder = os.path.abspath(self.images_folder)
        os.makedirs(abs_images_folder, exist_ok=True)
    
    # Room CRUD operations
    def get_all_rooms(self):
        """Get all rooms with room type information"""
        rooms = self.db.get_all_rooms()
        room_types = self.db.get_all_room_types()
        type_dict = {rt["typeID"]: rt for rt in room_types}
        
        # Enrich rooms with room type name
        enriched_rooms = []
        for room in rooms:
            room_copy = room.copy()
            room_type = type_dict.get(room.get("typeID"))
            if room_type:
                room_copy["typeName"] = room_type.get("typeName", "")
            else:
                room_copy["typeName"] = "Unknown"
            enriched_rooms.append(room_copy)
        
        return enriched_rooms
    
    def create_room(self, room_number, type_id, status="Available"):
        """
        Create a new room
        
        Args:
            room_number: Room number (must be unique)
            type_id: Room type ID
            status: Room status (default: Available)
            
        Returns:
            Room data if successful, None if room number already exists
        """
        # Check if room number already exists
        existing_room = self.db.get_room_by_number(room_number)
        if existing_room:
            return None
        
        # Get all rooms to generate new ID
        rooms = self.db.get_all_rooms()
        new_room_id = max([r.get("roomId", 0) for r in rooms], default=0) + 1
        
        room_data = {
            "roomId": new_room_id,
            "roomNumber": room_number,
            "typeID": type_id,
            "Status": status
        }
        
        self.db.add_room(room_data)
        return room_data
    
    def update_room(self, room_id, room_number=None, type_id=None, status=None):
        """
        Update room information
        
        Args:
            room_id: Room ID to update
            room_number: New room number (optional, must be unique if provided)
            type_id: New type ID (optional)
            status: New status (optional)
            
        Returns:
            True if successful, False if room number already exists or room not found
        """
        room = self.db.get_all_rooms()
        target_room = None
        for r in room:
            if r.get("roomId") == room_id:
                target_room = r
                break
        
        if not target_room:
            return False
        
        # Check room number uniqueness if changing
        if room_number and room_number != target_room.get("roomNumber"):
            existing_room = self.db.get_room_by_number(room_number)
            if existing_room:
                return False
        
        # Build update data
        update_data = {}
        if room_number is not None:
            update_data["roomNumber"] = room_number
        if type_id is not None:
            update_data["typeID"] = type_id
        if status is not None:
            update_data["Status"] = status
        
        self.db.update_room(room_id, update_data)
        return True
    
    def delete_room(self, room_id):
        """
        Delete a room
        
        Args:
            room_id: Room ID to delete
            
        Returns:
            True if successful, False if room not found or room is booked
        """
        rooms = self.db.get_all_rooms()
        target_room = None
        for r in rooms:
            if r.get("roomId") == room_id:
                target_room = r
                break
        
        if not target_room:
            return False
        
        # Check if room is booked - don't allow deletion of booked rooms
        if target_room.get("Status") == "Booked":
            return False
        
        self.db.delete_room(room_id)
        return True
    
    # Room Type CRUD operations
    def get_all_room_types(self):
        """Get all room types"""
        return self.db.get_all_room_types()
    
    def create_room_type(self, type_name, description, price, image_path):
        """
        Create a new room type
        
        Args:
            type_name: Room type name
            description: Room type description
            price: Price per night
            image_path: Path to image file (will be copied to assets/images)
            
        Returns:
            Room type data if successful, None if type name already exists
        """
        # Check if type name already exists
        room_types = self.db.get_all_room_types()
        for rt in room_types:
            if rt.get("typeName", "").lower() == type_name.lower():
                return None
        
        # Generate new type ID
        new_type_id = max([rt.get("typeID", 0) for rt in room_types], default=0) + 1
        
        # Handle image upload
        final_image_path = ""
        if image_path and os.path.exists(image_path):
            try:
                # Get file extension
                _, ext = os.path.splitext(image_path)
                # Create new filename
                new_filename = f"room_type_{new_type_id}{ext}"
                dest_path = os.path.join(self.images_folder, new_filename)
                
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy image to assets folder
                shutil.copy2(image_path, dest_path)
                
                # Normalize path to use forward slashes for cross-platform compatibility
                final_image_path = dest_path.replace("\\", "/")
            except Exception as e:
                # If copy fails, still create room type but without image
                print(f"Warning: Failed to copy image: {e}")
                final_image_path = ""
        
        type_data = {
            "typeID": new_type_id,
            "typeName": type_name,
            "description": description,
            "price": price,
            "imagePath": final_image_path
        }
        
        self.db.add_room_type(type_data)
        return type_data
    
    def update_room_type(self, type_id, type_name=None, description=None, price=None, image_path=None):
        """
        Update room type information
        
        Args:
            type_id: Type ID to update
            type_name: New type name (optional)
            description: New description (optional)
            price: New price (optional)
            image_path: New image path (optional, will be copied to assets/images)
            
        Returns:
            True if successful, False if type name already exists or type not found
        """
        room_types = self.db.get_all_room_types()
        target_type = None
        for rt in room_types:
            if rt.get("typeID") == type_id:
                target_type = rt
                break
        
        if not target_type:
            return False
        
        # Check type name uniqueness if changing
        if type_name and type_name.lower() != target_type.get("typeName", "").lower():
            for rt in room_types:
                if rt.get("typeID") != type_id and rt.get("typeName", "").lower() == type_name.lower():
                    return False
        
        # Build update data
        update_data = {}
        if type_name is not None:
            update_data["typeName"] = type_name
        if description is not None:
            update_data["description"] = description
        if price is not None:
            update_data["price"] = price
        
        # Handle image update
        if image_path and os.path.exists(image_path):
            try:
                # Get file extension
                _, ext = os.path.splitext(image_path)
                # Create new filename
                new_filename = f"room_type_{type_id}{ext}"
                dest_path = os.path.join(self.images_folder, new_filename)
                
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Copy image to assets folder
                shutil.copy2(image_path, dest_path)
                
                # Normalize path to use forward slashes for cross-platform compatibility
                update_data["imagePath"] = dest_path.replace("\\", "/")
            except Exception as e:
                # If copy fails, skip image update
                print(f"Warning: Failed to copy image: {e}")
        
        self.db.update_room_type(type_id, update_data)
        return True
    
    def delete_room_type(self, type_id):
        """
        Delete a room type
        
        Args:
            type_id: Type ID to delete
            
        Returns:
            True if successful, False if type not found or type is in use
        """
        # Check if any rooms are using this type
        rooms = self.db.get_all_rooms()
        for r in rooms:
            if r.get("typeID") == type_id:
                return False  # Cannot delete type that is in use
        
        self.db.delete_room_type(type_id)
        return True
    
    # Room Status operations
    def update_room_status(self, room_id, new_status):
        """
        Update room status
        
        Args:
            room_id: Room ID
            new_status: New status (can only change Available -> Cleaning/Maintenance, not to Booked)
            
        Returns:
            True if successful, False if invalid status change
        """
        rooms = self.db.get_all_rooms()
        target_room = None
        for r in rooms:
            if r.get("roomId") == room_id:
                target_room = r
                break
        
        if not target_room:
            return False
        
        current_status = target_room.get("Status", "")
        
        # Only allow changing Available -> Cleaning or Maintenance
        # Cannot change to Booked (that's done through bookings)
        if current_status == "Available" and new_status in ["Cleaning", "Maintenance"]:
            self.db.update_room_status(room_id, new_status)
            return True
        
        # Allow changing Cleaning/Maintenance back to Available
        if current_status in ["Cleaning", "Maintenance"] and new_status == "Available":
            self.db.update_room_status(room_id, new_status)
            return True
        
        return False
    
    def get_rooms_for_status_management(self):
        """Get all rooms with room type information for status management"""
        return self.get_all_rooms()

