"""If you have Ned Batchelder's coverage_ module installed, you may activate a
coverage report with the --with-coverage switch or NOSE_WITH_COVERAGE
environment variable. The coverage report will cover any python source module
imported after the start of the test run, excluding modules that match
testMatch. If you want to include those modules too, use the --cover-tests
switch, or set the NOSE_COVER_TESTS environment variable to a true value. To
restrict the coverage report to modules from a particular package or packages,
use the --cover-packages switch or the NOSE_COVER_PACKAGES environment
variable.

.. _coverage: http://www.nedbatchelder.com/code/modules/coverage.html
"""
import logging
import os
import sys
from nose.plugins.base import Plugin
from nose.util import tolist

log =  logging.getLogger(__name__)

class FuncCoverage(Plugin):
    """
    If you have Ned Batchelder's coverage module installed, you may
    activate a coverage report. The coverage report will cover any
    python source module imported after the start of the test run, excluding
    modules that match testMatch. If you want to include those modules too,
    use the --cover-tests switch, or set the NOSE_COVER_TESTS environment
    variable to a true value. To restrict the coverage report to modules from
    a particular package or packages, use the --cover-packages switch or the
    NOSE_COVER_PACKAGES environment variable.
    """
    coverTests = False
    coverPackages = None
    
    def options(self, parser, env=os.environ):
        Plugin.options(self, parser, env)
        parser.add_option("--func-cover-package", action="append",
                          default=env.get('FUNC_NOSE_COVER_PACKAGE'),
                          dest="cover_packages",
                          help="Restrict coverage output to selected packages "
                          "[FUNC_NOSE_COVER_PACKAGE]")
        parser.add_option("--func-cover-erase", action="store_true",
                          default=env.get('FUNC_NOSE_COVER_ERASE'),
                          dest="cover_erase",
                          help="Erase previously collected coverage "
                          "statistics before run")
        parser.add_option("--func-cover-tests", action="store_true",
                          dest="cover_tests",
                          default=env.get('FUNC_NOSE_COVER_TESTS'),
                          help="Include test modules in coverage report "
                          "[FUNC_NOSE_COVER_TESTS]")
        parser.add_option("--func-cover-annotate", action="store_true",
                          dest="cover_annotate",
                          help="write out annotated files"
                          "[FUNC_NOSE_COVER_ANNOTATE]"),
        parser.add_option("--func-cover-dir", action="store",
                          dest="cover_dir",
                          help="directory to write data to"
                          "[FUNC_NOSE_COVER_DIR]"),

        parser.add_option("--func-cover-inclusive", action="store_true",
                          dest="cover_inclusive",
                          default=env.get('FUNC_NOSE_COVER_INCLUSIVE'),
                          help="Include all python files under working "
                          "directory in coverage report.  Useful for "
                          "discovering holes in test coverage if not all "
                          "files are imported by the test suite. "
                          "[FUNC_NOSE_COVER_INCLUSIVE]")
        

    def configure(self, options, config):
        Plugin.configure(self, options, config)
        if self.enabled:
            try:
                import coverage
            except ImportError:
                log.error("Coverage not available: "
                          "unable to import coverage module")
                self.enabled = False
                return
        self.conf = config
        self.coverErase = options.cover_erase
        self.coverTests = options.cover_tests
        self.coverPackages = []
        self.coverDir = options.cover_dir
        self.coverAnnotate = options.cover_annotate
        if options.cover_packages:
            for pkgs in [tolist(x) for x in options.cover_packages]:
                self.coverPackages.extend(pkgs)
        self.coverInclusive = options.cover_inclusive
        if self.coverPackages:
            log.info("Coverage report will include only packages: %s",
                     self.coverPackages)
            
    def begin(self):
        log.debug("Coverage begin")
        import coverage
        self.skipModules = sys.modules.keys()[:]
        if self.coverErase:
            log.debug("Clearing previously collected coverage statistics")
            coverage.erase()
        coverage.exclude('#pragma[: ]+[nN][oO] [cC][oO][vV][eE][rR]')
        coverage.start()
        
    def report(self, stream):
        log.debug("Coverage report")
        import coverage
        coverage.stop()
        modules = [ module
                    for name, module in sys.modules.items()
                    if self.wantModuleCoverage(name, module) ]
        log.debug("Coverage report will cover modules: %s", modules)
        if self.coverDir and self.coverAnnotate:
            coverage.annotate(modules, self.coverDir)
        fd = open("%s/cover.report" % self.coverDir, "w")
        coverage.report(modules, file=fd)
        fd.close()

    def wantModuleCoverage(self, name, module):
        if not hasattr(module, '__file__'):
            log.debug("no coverage of %s: no __file__", name)
            return False
        root, ext = os.path.splitext(module.__file__)
        if not ext in ('.py', '.pyc', '.pyo'):
            log.debug("no coverage of %s: not a python file", name)
            return False
        if self.coverPackages:
            for package in self.coverPackages:
                if (name.startswith(package)
                    and (self.coverTests
                         or not self.conf.testMatch.search(name))):
                    log.debug("coverage for %s", name)
                    return True                
        if name in self.skipModules:
            log.debug("no coverage for %s: loaded before coverage start",
                      name)
            return False
        if self.conf.testMatch.search(name) and not self.coverTests:
            log.debug("no coverage for %s: is a test", name)
            return False
        # accept any package that passed the previous tests, unless
        # coverPackages is on -- in that case, if we wanted this
        # module, we would have already returned True
        return not self.coverPackages

    def wantFile(self, file, package=None):    
        """If inclusive coverage enabled, return true for all source files 
        in wanted packages.
        """
        if self.coverInclusive:
            if file.endswith(".py"): 
                if package and self.coverPackages:
                    for want in self.coverPackages:
                        if package.startswith(want):
                            return True
                else:
                    return True
        return None
    
