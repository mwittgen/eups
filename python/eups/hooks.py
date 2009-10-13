"""
Module that enables user configuration and hooks.  
"""
import os, sys, re
import utils
from VersionCompare import VersionCompare

# the function to use to compare two version.  The user may reset this 
# to provide a different algorithm.
version_cmp = VersionCompare()

# a function for setting fallback flavors.  This function is callable by 
# the user.  
setFallbackFlavors = utils.Flavor().setFallbackFlavors

# various configuration properties settable by the user
config = utils.ConfigProperty("Eups".split())
config.Eups = utils.ConfigProperty("verbose userTags setupTypes setupCmdName".split(), "Eups")
config.Eups.setType("verbose", int)

config.Eups.verbose = 0
config.Eups.userTags = ""
config.Eups.setupTypes = "build"
config.Eups.setupCmdName = "setup"

    
startupFileName = "startup.py"
configFileName = "config.txt"

def loadCustomizationFromDir(customDir, verbose=0, log=sys.stderr):
    cfile = os.path.join(customDir, configFileName)
    if os.path.exists(cfile):
        if verbose > 0:
            print >> log, "loading properties from", cfile
        loadConfigProperties(cfile)

    startup = os.path.join(customDir, configFileName) 
    if os.path.exists(startup):
        execfile(startup)

def loadCustomization(verbose=0, log=sys.stderr):
    """
    load all site and/or user customizations.  Customizations can come in two
    forms: a configuration properties file and/or a startup script file.  
    Any customizations that appears in a startup script file will override
    those found in the properties file.
    @param customDir    a directory where customization files can be found
    """
    customDirs = []

    # a site-leve directory can have configuration stuff in it
    if os.environ.has_key("EUPS_SITEDATA"):
        customDirs.append(os.environ["EUPS_SITEDATA"])

    # $HOME/.eups can have user configuration stuff in it
    if os.environ.has_key("EUPS_USERDATA"):
        customDirs.append(os.environ["EUPS_USERDATA"])
    elif os.environ.has_key("HOME"):
        customDirs.append(os.path.join(os.environ["HOME"], ".eups"))

    # load the configuration by directories; later ones override prior ones
    for dir in customDirs:
        loadCustomizationFromDir(dir)

    # load any custom startup scripts via EUPS_STARTUP; this overrides
    # everything
    if os.environ.has_key("EUPS_STARTUP"):
        for startupFile in os.environ["EUPS_STARTUP"].split(':'):
            if os.path.exists(startupFile):
                try:
                    execfile(startupFile)
                except Exception, e:
                    raise CustomizationError(str(e))




commre = re.compile(r'#.*$')
namevalre = re.compile(r'[:=]')
def loadConfigProperties(configFile):
    maxerr = 5
    if not os.path.exists(configFile):
        return

    fd = open(configFile)
    lineno = 0
    try: 
        for line in fd:
            lineno += 1
            line = commre.sub('', line).strip()
            if not line:
                continue
            parts = namevalre.split(line, 1)
            if len(parts) != 2:
                if verbose >= 0 and maxerr > 0:
                    print >> log, "Bad property syntax (ignoring):", line
                    maxerr -= 1
                continue
            name, val = parts

            # turn property name into an attribute of hooks.config
            parts = name.split('.')
            attr = hooks.config
            while len(parts) > 1:
                nxt = parts.pop(0)
                if not hasattr(attr, nxt):
                    if verbose >= 0:
                      print >> log, "Ignoring unrecognized property:", name
                    break
                attr = getattr(attr, nxt)

            try:
                setattr(attr, parts[0], val)
            except AttributeError, e:
                if verbose >= 0:
                   print >> log, "Skipping bad property assignment:", str(e)

    finally:
        fd.close()


_validSetupTypes = {}   # in lieu of a set

def defineValidSetupTypes(*types):
    """Define a permissible type of setup (e.g. build)"""

    for tp in types:
        _validSetupTypes[tp] = 1

def getValidSetupTypes():
    """Return (a copy of) all valid types of setup (e.g. build)"""
    out = _validSetupTypes.keys()
    out.sort()
    return out

