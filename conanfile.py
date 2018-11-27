from conans import ConanFile, CMake, tools
from conanos.build import config_scheme
import os
import shutil


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    version = "2.1.3"
    description = "HarfBuzz is an OpenType text shaping engine."
    url = "https://github.com/conanos/harfbuzz"
    homepage = "http://harfbuzz.org/"
    license = "MIT"
    patch = "copyright-character-gbk-encode-error.patch"
    exports = ["FindHarfBuzz.cmake", "LICENSE.md", patch]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'with_freetype': [True, False]
    }
    default_options = { 'shared': False, 'fPIC': True, 'with_freetype': True }
    generators = "cmake"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        if self.options.with_freetype:
            self.requires.add("freetype/2.9.1@conanos/stable")

        self.requires.add("fontconfig/2.13.0@conanos/stable")
        self.requires.add("cairo/1.15.12@conanos/stable")
        self.requires.add("glib/2.58.1@conanos/stable")

        config_scheme(self)
    
    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("bzip2/1.0.6@conanos/stable")
            self.build_requires("libpng/1.6.34@conanos/stable")
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        
    
    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        url_ = 'https://github.com/harfbuzz/harfbuzz/archive/{version}.tar.gz'.format(version=self.version)
        tools.get(url_)
        if self.settings.os == "Windows":
            tools.patch(patch_file=self.patch)
        os.rename(self.name+"-"+self.version, self._source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["fontconfig","cairo","glib"] ]
        if self.options.with_freetype:
            pkg_config_paths.extend([ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["freetype"] ])
            cmake.definitions["CMAKE_PREFIX_PATH"] = os.path.join(self.deps_cpp_info["freetype"].rootpath)

        cmake.definitions["HB_HAVE_FREETYPE"] = self.options.with_freetype
        cmake.definitions["HB_HAVE_GLIB"] = True
        if self.settings.os == "Linux":
            cmake.definitions["HB_BUILD_UTILS"] = True
            cmake.definitions["PC_CAIRO_INCLUDE_DIRS"] = os.path.join(self.deps_cpp_info["cairo"].rootpath, "include")
            cmake.definitions["PC_CAIRO_LIBDIR"] = os.path.join(self.deps_cpp_info["cairo"].rootpath, "lib")
        cmake.definitions["HB_HAVE_GOBJECT"] = True
        cmake.definitions["PC_glib_mkenums"] =  os.path.join(self.deps_cpp_info["glib"].rootpath, "bin") #for glib-mkenums
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if self.settings.os == "Linux":
            cmake.definitions['CONAN_CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder,pkg_config_paths=pkg_config_paths)
        return cmake

    def build(self):
        include = [ os.path.join(self.deps_cpp_info[i].rootpath, "include") for i in ["fontconfig"] ]
        libpath=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib") for i in ["bzip2", "libpng"] ]
        if self.settings.os == "Linux":
            tools.mkdir(os.path.join(self.build_folder, self._build_subfolder, "src"))
        if self.settings.os == "Linux":
            env_vars = {
                "LD_LIBRARY_PATH" : os.pathsep.join(libpath),
                "CPLUS_INCLUDE_PATH" : include,
                }
        if self.settings.os == "Windows":
            env_vars = {
                "INCLUDE" : os.pathsep.join(include + [os.getenv('INCLUDE')]),
                }
        with tools.environment_append(env_vars):
            cmake = self.configure_cmake()
            cmake.build()
            cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
