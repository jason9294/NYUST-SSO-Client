class CaptchaError(Exception):
    """Exception raised for errors related to captcha verification."""

    def __init__(self, message="Captcha verification failed"):
        self.message = message
        super().__init__(self.message)


class AccessDenyError(Exception):
    """Exception raised for errors related to access denied."""

    def __init__(self, message="Access denied"):
        self.message = message
        super().__init__(self.message)
