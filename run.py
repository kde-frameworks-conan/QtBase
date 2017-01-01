from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    for shared in [True, False]:
        for build_type in ["Debug", "Release"]:
            for gccver in builder.gcc_versions:
                builder.add({"arch": "x86_64",
                            "build_type": build_type,
                            "compiler": "gcc",
                            "compiler.version": gccver,
                            "compiler.libcxx": "libstdc++11"},
                            {"QtBase:shared": shared})

    builder.run()
