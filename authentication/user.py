class User:
    def __init__(self, name, password, profile_pic=None):
        self.name = name
        self.password = password
        self.profile_pic = profile_pic  # Path to profile picture, or None to use letter avatar