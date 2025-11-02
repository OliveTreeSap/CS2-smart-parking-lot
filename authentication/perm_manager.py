class PermissionManager:
    def __init__(self, db="database.txt"):
        self.db = db

    def authenticator(self, name, password):
        """Reads the "database" to find any matching username and password"""
        with open(self.db, "r") as users:
            for user in users:
                if [name, password] == user.strip().split(", "):
                    return True
                

if __name__ == "__main__":
    test = PermissionManager()