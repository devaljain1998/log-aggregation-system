class InvalidSearchParameterException(Exception):
    def __init__(self, message: str = "At least one search parameter is required"):
        self.message = message
        super().__init__(self.message)
