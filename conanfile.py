from conans import ConanFile, CMake, tools#, AutoToolsBuildEnvironment
import os

class LibcrocoConan(ConanFile):
    name = "libcroco"
    version = "0.6.12"
    description = "Libcroco is a general CSS parsing and manipulation library written in C for the GNOME project"
    url = "https://github.com/conan-multimedia/libcroco"
    homepage = "https://launchpad.net/libcroco"
    license = "LGPLv2_1"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    source_subfolder = "source_subfolder"
    requires = ("libxml2/2.9.8@conanos/dev", "glib/2.58.0@conanos/dev", "gdk-pixbuf/2.36.2@conanos/dev",
                "libffi/3.3-rc0@conanos/dev")

    def source(self):
        maj_ver = '.'.join(self.version.split('.')[0:2])
        tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'http://ftp.gnome.org/pub/GNOME/sources/%s/%s/%s'%(self.name, maj_ver, archive_name)
        tools.download(url_, archive_name)
        
        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('%s-%s'%(self.name, self.version) , self.source_subfolder)
        os.unlink(archive_name)

    def build(self):
        #vars = {'PKG_CONFIG_PATH': "%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig"
        #%(self.deps_cpp_info["libffi"].rootpath,self.deps_cpp_info["glib"].rootpath,
        #self.deps_cpp_info["gdk-pixbuf"].rootpath,self.deps_cpp_info["libxml2"].rootpath)}

        #with tools.environment_append(vars):
        #    self.run("./configure --prefix %s/build --libdir %s/build/lib --enable-introspection"%(os.getcwd(),os.getcwd()))
        #    self.run("make -j4")
        #    self.run("make install")
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH' : '%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
                %(self.deps_cpp_info["libxml2"].rootpath,self.deps_cpp_info["glib"].rootpath,
                self.deps_cpp_info["gdk-pixbuf"].rootpath,self.deps_cpp_info["libffi"].rootpath,)
                }):

                _args = ["--prefix=%s/builddir"%(os.getcwd())]
                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])

                self.run("./configure %s"%(' '.join(_args)))
                self.run("make -j4")
                self.run("make install")
                #autotools = AutoToolsBuildEnvironment(self)
                #autotools.configure(args=_args)
                #autotools.make(args=["-j4"])
                #autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

