# -*- coding: utf-8 -*-
"""
WinPython build script

Created on Sun Aug 12 11:17:50 2012
"""

import os
import os.path as osp
import re
import subprocess
import shutil

# Local imports
from winpython import wppm


#==============================================================================
# The batch to exe conversion is abandoned due to false virus detection issues
#==============================================================================
def bat_to_exe(fname, icon):
    """Convert .bat file to .exe using Bat_To_Exe_Converter (www.f2ko.de)"""
    conv = 'Bat_To_Exe_Converter.exe'
    assert fname.endswith('.bat')
    assert icon.endswith('.ico')
    #assert wppm.is_program_installed(conv)
    bname = osp.basename(fname)
    args = ['-bat', bname, '-save', bname.replace('.bat', '.exe')]#,
#            '-icon', osp.abspath(icon)]
    print args
    subprocess.call([conv]+args, cwd=osp.dirname(fname))

def call_bat_from_exe(batname, targetname, icon):
    """Call .bat file from a generated .exe file
    Executable file is created in .bat file parent directory"""
    assert batname.endswith('.bat')
    assert targetname.endswith('.exe')
    assert icon.endswith('.ico') and osp.isfile(icon)
    exedir = osp.join(osp.dirname(batname), os.pardir)
    exename = osp.join(exedir, targetname)
    tmpbatname = exename.replace('.exe', '-tmp.bat')
    tmpbat = file(tmpbatname, 'w')
    tmpbat.write("""@echo off
call %s""" % osp.relpath(batname, exedir))
    tmpbat.close()
    bat_to_exe(tmpbatname, icon)

def bat_to_exe_test():
    wpdir = osp.join(osp.dirname(__file__), os.pardir, 'sandbox',
                     'winpython-2.7.3.amd64')
    call_bat_from_exe(osp.join(wpdir, 'scripts', 'spyder.bat'), 'Spyder.exe',
                      osp.join(wpdir, 'python-2.7.3.amd64',
                               'Scripts', 'spyder.ico'))
        

class WinPythonDistribution(object):
    """WinPython distribution"""
    def __init__(self, target, instdir):
        self.target = target
        self.instdir = instdir
        self.version = None
        self.fullversion = None
        self.winpydir = None
        self.distribution = None
        self.installed_packages = []
        
    def get_package_fname(self, pattern):
        """Get package matching pattern in instdir"""
        for fname in os.listdir(self.instdir):
            match = re.match(pattern, fname)
            if match is not None:
                return osp.abspath(osp.join(self.instdir, fname))
        else:
            raise RuntimeError, 'Could not found required package matching %s' % pattern
    
    def install_package(self, pattern):
        """Install package matching pattern"""
        fname = self.get_package_fname(pattern)
        bname = osp.basename(fname)
        if bname not in self.installed_packages:
            pack = wppm.Package(fname)
            self.distribution.install(pack)
            self.installed_packages.append(bname)

    def create_batch_script(self, name, contents):
        """Create batch script %WINPYDIR%/name"""
        assert name.endswith('.bat')
        scriptdir = osp.join(self.winpydir, 'scripts')
        if not osp.isdir(scriptdir):
            os.mkdir(scriptdir)
        fd = file(osp.join(scriptdir, name), 'w')
        fd.write(contents)
        fd.close()
    
    def make(self):
        """Make WinPython distribution in target directory from the installers 
        located in instdir"""
        python_fname = self.get_package_fname(r'python-([0-9\.]*)')
        python_name = osp.basename(python_fname)[:-4]
        distname = 'win%s' % python_name
        vlst = re.match(r'winpython-([0-9\.]*)', distname
                        ).groups()[0].split('.')
        self.version = '.'.join(vlst[:2])
        self.fullversion = '.'.join(vlst[:3])
        
        # Create the WinPython base directory
        wppm.print_box("Creating WinPython base directory")
        self.winpydir = osp.join(self.target, distname)
        if osp.isdir(self.winpydir):
            shutil.rmtree(self.winpydir)
        os.mkdir(self.winpydir)

        # Extracting Python installer, creating distribution object
        wppm.print_box("Extracting Python installer")
        wppm.extract_msi(python_fname, targetdir=self.winpydir)
        self.installed_packages.append(python_fname)
        pydir = osp.join(self.winpydir, python_name)
        self.distribution = wppm.Distribution(pydir)
        os.mkdir(osp.join(pydir, 'Scripts'))
        
        # Install winpython package (wppm)
        wppm.print_box("Installing WinPython package")
        shutil.copytree(osp.join(osp.dirname(__file__), 'winpython'),
                        osp.join(pydir, 'Lib', 'site-packages', 'winpython'))
        
        # Install PyQt and PyQwt
        arch1 = 'x64' if 'amd64' in distname else 'x86'
        self.install_package(pattern='PyQt-Py%s-%s-gpl-([0-9\.\-]*).exe'
                                     % (self.version, arch1))
        file(osp.join(pydir, 'qt.conf'), 'w').write("""[Paths]
Prefix = ./Lib/site-packages/PyQt4
Binaries = ./Lib/site-packages/PyQt4""")
        self.install_package(
                    pattern='PyQwt-([0-9\.]*)-py%s-%s-([a-z0-9\.\-]*).exe'
                            % (self.version, arch1))

        # Install pywin32
        arch2 = 'win-amd64' if 'amd64' in distname else 'win32'
        self.install_package('pywin32-([0-9]*).%s-py%s.exe'
                             % (arch2, self.version))
        
        # Try to install all other packages in instdir
        for fname in os.listdir(self.instdir):
            try:
                self.install_package(fname)
            except NotImplementedError:
                pass
        
        # Show stats
        wppm.print_box("Installed packages")
        for fname in self.installed_packages:
            print "   ", fname
        
        # Copy dev tools
        wppm.print_box("Copying tools")
        shutil.copytree(osp.join(osp.dirname(__file__), 'tools'),
                        osp.join(self.winpydir, 'tools'))

        # Create batch scripts
        self.create_batch_script('cmd.bat', r"""@echo off
call %~dp0env.bat
cmd.exe /k""")
        self.create_batch_script('env.bat', """@echo off
set WINPYDIR=%~dp0..\\""" + python_name + r"""
set PATH=%WINPYDIR%\Lib\site-packages\pywin32_system32;%PATH%
set PATH=%WINPYDIR%\Lib\site-packages\PyQt4;%PATH%
set PATH=%PATH%;%WINPYDIR%\;%WINPYDIR%\DLLs;%WINPYDIR%\Scripts
set PATH=%PATH%;%~dp0..\tools;%~dp0..\tools\gnuwin32\bin
set PATH=%PATH%;%~dp0..\tools\TortoiseHg-"""+arch1)
        self.create_batch_script('python.bat', r"""@echo off
call %~dp0env.bat
%WINPYDIR%\python.exe %*""")
        self.create_batch_script('spyder.bat', r"""@echo off
call %~dp0env.bat
cd %WINPYDIR%\Lib\site-packages\spyderlib
%WINPYDIR%\python.exe spyder.py %*""")
        self.create_batch_script('spyder_light.bat', r"""@echo off
call "%~dp0spyder.bat" --light""")

        self.distribution.clean_up()
    

if __name__ == '__main__':
    sbdir = osp.join(osp.dirname(__file__), os.pardir, 'sandbox')
    sbdir = r'D:\Pierre'
    wpdir = osp.join(sbdir, 'maketest')
    instdir = osp.join(sbdir, 'installers')
    if not osp.isdir(wpdir):
        os.mkdir(wpdir)
    dist = WinPythonDistribution(wpdir, instdir)
    dist.make()