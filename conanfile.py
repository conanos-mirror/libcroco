from conans import ConanFile, tools, MSBuild
from conanos.build import config_scheme
import os, shutil, sys

class LibcrocoConan(ConanFile):
    name = "libcroco"
    version = "0.6.12"
    description = "Libcroco is a general CSS parsing and manipulation library written in C for the GNOME project"
    url = "https://github.com/conanos/libcroco"
    homepage = "https://launchpad.net/libcroco"
    license = "LGPL-v2.1"
    exports = ["COPYING"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    #requires = ("libxml2/2.9.8@conanos/dev", "glib/2.58.0@conanos/dev", "gdk-pixbuf/2.36.2@conanos/dev",
    #            "libffi/3.3-rc0@conanos/dev")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("libxml2/2.9.8@conanos/stable")
        self.requires.add("glib/2.58.1@conanos/stable")
        self.requires.add("gdk-pixbuf/2.38.0@conanos/stable")

    def build_requirements(self):
        self.build_requires("libiconv/1.15@conanos/stable")
        if self.settings.os == 'Windows':
            self.build_requires("7z_installer/1.0@conan/stable")

    def source(self):
        maj_ver = '.'.join(self.version.split('.')[0:2])
        tarball_name = 'libcroco-{version}.tar'.format(version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'http://ftp.gnome.org/pub/GNOME/sources/libcroco/{maj_ver}/{archive_name}'
        tools.download(url_.format(maj_ver=maj_ver,archive_name=archive_name), archive_name)
        
        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        os.unlink(archive_name)

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    with tools.environment_append({
        #        'PKG_CONFIG_PATH' : '%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig'
        #        %(self.deps_cpp_info["libxml2"].rootpath,self.deps_cpp_info["glib"].rootpath,
        #        self.deps_cpp_info["gdk-pixbuf"].rootpath,self.deps_cpp_info["libffi"].rootpath,)
        #        }):

        #        _args = ["--prefix=%s/builddir"%(os.getcwd())]
        #        if self.options.shared:
        #            _args.extend(['--enable-shared=yes','--enable-static=no'])
        #        else:
        #            _args.extend(['--enable-shared=no','--enable-static=yes'])

        #        self.run("./configure %s"%(' '.join(_args)))
        #        self.run("make -j4")
        #        self.run("make install")
        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder,"win32","vs15")):
                replacements = {
                    "<PythonPath>c:\python34</PythonPath>": "<PythonPath>%s</PythonPath>"%(os.path.dirname(sys.executable))
                }
                for s, r in replacements.items():
                    tools.replace_in_file("croco-version-paths.props",s,r,strict=True)
                tools.out.info("------------------%s,        %s"%(sys.executable,os.path.dirname(sys.executable)))

                msbuild = MSBuild(self)
                msbuild.build("libcroco.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})
                

    def package(self):
        if self.settings.os == 'Windows':
            platforms = {'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join("vs15",platforms.get(str(self.settings.arch)))
            self.copy("*", dst=os.path.join(self.package_folder),src=os.path.join(self.build_folder,output_rpath))

        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

