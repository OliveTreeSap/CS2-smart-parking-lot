import os
from authentication.user import User


class PermissionManager:
    def __init__(self, db="database/user.txt", profile_img_dir="database/user_profile_img"):
        self.db = db
        self.profile_img_dir = profile_img_dir

    def authenticator(self, name, password):
        """Reads the "database" to find any matching username and password"""
        with open(self.db, "r") as users:
            for user in users:
                if [name, password] == user.strip().split(", "):
                    return True
    
    def get_all_users(self):
        """Returns a list of all usernames from the database"""
        usernames = []
        with open(self.db, "r") as users:
            for user in users:
                username = user.strip().split(", ")[0]
                usernames.append(username)
        return usernames
    
    def get_user_objects(self):
        """Returns a list of User objects with profile pictures"""
        user_objects = []
        with open(self.db, "r") as users:
            for idx, user in enumerate(users, 1):
                parts = user.strip().split(", ")
                username = parts[0]
                password = parts[1]
                
                # Try to find profile picture
                profile_pic = self._find_profile_pic(username, idx)
                
                user_obj = User(username, password, profile_pic)
                user_objects.append(user_obj)
        
        return user_objects
    
    def _find_profile_pic(self, username, user_index):
        """Find profile picture for a user. Returns path or None."""
        # Try different naming patterns
        patterns = [
            f"user_{user_index}.png",
            f"user_{user_index}.jpg",
            f"{username}.png",
            f"{username}.jpg"
        ]
        
        for pattern in patterns:
            img_path = os.path.join(self.profile_img_dir, pattern)
            if os.path.exists(img_path):
                return img_path
        
        return None  # No image found, will use letter avatar
                

if __name__ == "__main__":
    test = PermissionManager()