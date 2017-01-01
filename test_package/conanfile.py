from conans import CMake, ConanFile
import os


channel = os.getenv("CONAN_CHANNEL", "stable")
username = os.getenv("CONAN_USERNAME", "russelltg")


class DefaultNameConan(ConanFile):
    name="QtBaseTest"
    requires = "QtBase/5.7.1@%s/%s" % (username, channel)

    def build(self):
        pass
    
    def test(self):
        pass
    
