import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


TESTS_REQUIRE = ['tox >= 2.3']


setup(
    name='djangocms_plus',
    version='0.1.11',
    author='InQuant GmbH',
    author_email='info@inquant.de',
    packages=['cmsplus'],
    url='https://github.com/domlysi/djangocms_plus',
    license='MIT',
    description='Lightweight rewrite for DjangoCMS Plugins to store plugin data in JSON.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README.md'], },
    install_requires=['django-cms>=3.7.1', 'django-jsonfield', 'django-filer', 'easy_thumbnails', 'django>=2.2.12'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django CMS',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    tests_require=TESTS_REQUIRE,
    extras_require={
        'cmsplus_tests': TESTS_REQUIRE,
    },
    cmdclass={'cmsplus_tests': Tox}
)
