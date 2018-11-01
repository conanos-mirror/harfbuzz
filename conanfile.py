from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from shutil import copyfile
import os


class HarfbuzzConan(ConanFile):
    name = "harfbuzz"
    version = "1.7.5"
    description = "HarfBuzz is an OpenType text shaping engine."
    url = "https://github.com/conanos/harfbuzz"
    homepage = "http://harfbuzz.org/"
    license = "MIT"
    exports = ["LICENSE.md"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'with_freetype': [True, False]
    }
    default_options = ("shared=True", "fPIC=True", "with_freetype=True")
    generators = "cmake"
    requires = ("fontconfig/2.12.6@conanos/dev","cairo/1.14.12@conanos/dev","glib/2.58.0@conanos/dev",
    "freetype/2.9.0@conanos/dev",
    "pixman/0.34.0@conanos/dev",#required by 'cairo' 
    "libpng/1.6.34@conanos/dev"#required by 'freetype2'
    )

    source_subfolder = "source_subfolder"

    def source(self):
        url_ = 'http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-{version}.tar.bz2'.format(version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH': ':%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
                %(self.deps_cpp_info['fontconfig'].rootpath,
                self.deps_cpp_info['cairo'].rootpath,
                self.deps_cpp_info['glib'].rootpath,
                self.deps_cpp_info['freetype'].rootpath,
                self.deps_cpp_info['pixman'].rootpath,
                self.deps_cpp_info['libpng'].rootpath,
                )}):
                
                _args = ['--prefix=%s/builddir'%(os.getcwd()), '--libdir=%s/builddir/lib'%(os.getcwd()),
                    '--disable-silent-rules', '--enable-introspection', '--with-icu=no',]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])
                if self.options.with_freetype:
                    _args.extend(['--with-freetype=yes'])
                else:
                    _args.extend(['--with-freetype=no'])

                self.run('./configure %s'%(' '.join(_args)))#space
                self.run('make -j2')
                self.run('make install')


    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
