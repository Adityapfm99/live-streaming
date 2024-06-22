from django.core.mail.backends.smtp import EmailBackend
import ssl
import certifi

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    def open(self):
        if self.connection:
            return False
        connection_params = {
            'host': self.host,
            'port': self.port,
            'local_hostname': self.local_hostname,
            'timeout': self.timeout,
            'ssl_context': self.ssl_context
        }
        self.connection = self.connection_class(**connection_params)
        self.connection.set_debuglevel(self.debug_level)
        if self.username and self.password:
            self.connection.login(self.username, self.password)
        return True
