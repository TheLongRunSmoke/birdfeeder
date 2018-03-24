from  abc import ABCMeta, abstractmethod


class ICamera:
    __metaclass__ = ABCMeta

    @abstractmethod
    def retrieve(self):
        """Return next frame from camera."""

    @abstractmethod
    def auto_exposure(self, frame):
        """Calculate and set exposure."""

    @abstractmethod
    def get_exposure(self):
        """Return current exposure."""
