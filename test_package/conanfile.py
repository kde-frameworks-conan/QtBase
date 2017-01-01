from conans import CMake, ConanFile
import os


channel = os.getenv("CONAN_CHANNEL", "stable")
username = os.getenv("CONAN_USERNAME", "russelltg")


class DefaultNameConan(ConanFile):
    name="QtBaseTest"
    requires = "QtBase/5.7.1@%s/%s" % (username, channel)
    generators="cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run("cmake {} {}".format(self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . {}".format(cmake.build_config))
    
    def test(self):
        self.run("./bin/qtbasetest")
    
