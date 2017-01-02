import os
from distutils.spawn import find_executable
from conans import ConanFile, ConfigureEnvironment
from conans.tools import cpu_count, vcvars_command, os_info, SystemPackageTool, download, untargz

class QtBaseConan(ConanFile):
    """ Qt Base Conan package """

    name = "QtBase"
    version = "5.7.1"
    majorVersion = "5.7"
    settings = "os", "arch", "compiler", "build_type"
    url = "http://github.com/kde-frameworks-conan/{}".format(name.lower())
    license = "http://doc.qt.io/qt-5/lgpl.html"
    short_paths = True
    
    options = {"shared": [True, False], "opengl": ["desktop", "dynamic"]}
    default_options = "shared=True", "opengl=desktop"

    
    
    folderName = "{}-opensource-src-{}".format(name.lower(), version)

    def system_requirements(self):
        pack_names = None
        if os_info.linux_distro == "ubuntu":
            pack_names = ["libgl1-mesa-dev", "libxcb1", "libxcb1-dev",
                          "libx11-xcb1", "libx11-xcb-dev", "libxcb-keysyms1",
                          "libxcb-keysyms1-dev", "libxcb-image0", "libxcb-image0-dev",
                          "libxcb-shm0", "libxcb-shm0-dev", "libxcb-icccm4",
                          "libxcb-icccm4-dev", "libxcb-sync1", "libxcb-sync-dev",
                          "libxcb-xfixes0-dev", "libxrender-dev", "libxcb-shape0-dev",
                          "libxcb-randr0-dev", "libxcb-render-util0", "libxcb-render-util0-dev",
                          "libxcb-glx0-dev", "libxcb-xinerama0", "libxcb-xinerama0-dev"]

            if self.settings.arch == "x86":
                full_pack_names = []
                for pack_name in pack_names:
                    full_pack_names += [pack_name + ":i386"]
                pack_names = full_pack_names

        if pack_names:
            installer = SystemPackageTool()
            installer.update() # Update the package database
            installer.install(" ".join(pack_names)) # Install the package

    def source(self):
        zipName = "{}.tar.gz".format(self.folderName)
        zipUrl = "http://download.qt.io/official_releases/qt/{}/{}/submodules/{}".format(self.majorVersion, self.version, zipName)
        download(zipUrl, zipName)
        untargz(zipName)
        os.unlink(zipName)
        

    def build(self):

        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        args = ["-opensource", "-confirm-license", "-nomake examples", "-nomake tests",
                "-prefix %s" % self.package_folder]
        if not self.options.shared:
            args.insert(0, "-static")
        if self.settings.build_type == "Debug":
            args.append("-debug")
        else:
            args.append("-release")

        if self.settings.os == "Macos":
            args.append("-no-framework")

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                self._build_msvc(args)
            else:
                self._build_mingw(args)
        else:
            self._build_unix(args)

    def _build_msvc(self, args):
        build_command = find_executable("jom.exe")
        if build_command:
            build_args = ["-j", str(cpu_count())]
        else:
            build_command = "nmake.exe"
            build_args = []
        self.output.info("Using '%s %s' to build" % (build_command, " ".join(build_args)))

        set_env = 'SET PATH={dir}/qtbase/bin;{dir}/gnuwin32/bin;%PATH%'.format(dir=self.conanfile_directory)
        args += ["-opengl %s" % self.options.opengl]
        # it seems not enough to set the vcvars for older versions, it works fine
        # with MSVC2015 without -platform
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version == "12":
                args += ["-platform win32-msvc2013"]
            if self.settings.compiler.version == "11":
                args += ["-platform win32-msvc2012"]
            if self.settings.compiler.version == "10":
                args += ["-platform win32-msvc2010"]

        vcvars = vcvars_command(self.settings)
        vcvars = vcvars + " && " if vcvars else ""
        
        self.run("cd %s && %s && %s configure %s"
                 % (self.folderName, set_env, vcvars, " ".join(args)))
        self.run("cd %s && %s %s %s"
                 % (self.folderName, vcvars, build_command, " ".join(build_args)))
        self.run("cd %s && %s %s install" % (self.folderName, vcvars, build_command))

    def _build_mingw(self, args):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        args += ["-developer-build", "-opengl %s" % self.options.opengl, "-platform win32-g++"]

        self.output.info("Using '%s' threads" % str(cpu_count()))
        self.run("%s && cd %s && configure.bat %s"
                 % (env.command_line_env, self.folderName, " ".join(args)))
        self.run("%s && cd %s && mingw32-make -j %s"
                 % (env.command_line_env, self.folderName, str(cpu_count())))
        self.run("%s && cd %s && mingw32-make install" % (env.command_line_env, self.folderName))

    def _build_unix(self, args):
        if self.settings.os == "Linux":
            args += ["-silent", "-xcb"]
            if self.settings.arch == "x86":
                args += ["-platform linux-g++-32"]
        else:
            args += ["-silent"]
            if self.settings.arch == "x86":
                args += ["-platform macx-clang-32"]

        self.output.info("Using '%s' threads" % str(cpu_count()))
        self.run("cd %s && ./configure %s" % (self.folderName, " ".join(args)))
        self.run("cd %s && make -j %s" % (self.folderName, str(cpu_count())))
        self.run("cd %s && make install" % (self.folderName))

    def package_info(self):
        libs = ['Concurrent', 'Core', 'DBus',
                'Gui', 'Network', 'OpenGL',
                'Sql', 'Test', 'Widgets', 'Xml']
        
        # add qmake etc to path
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))

        self.cpp_info.libs = []
        self.cpp_info.includedirs = ["include"]
        for lib in libs:
            if self.settings.os == "Windows" and self.settings.build_type == "Debug":
                suffix = "d"
            else:
                suffix = ""
            self.cpp_info.libs += ["Qt5%s%s" % (lib, suffix)]
            self.cpp_info.includedirs += ["include/Qt%s" % lib]

        if self.settings.os == "Windows":
            # Some missing shared libs inside QML and others, but for the test it works
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))
