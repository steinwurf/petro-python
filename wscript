#! /usr/bin/env python
# encoding: utf-8

import os

APPNAME = 'petro-python'
VERSION = '1.0.0'


def options(opt):

    opt.load('python')


def build(bld):

    # Ensure that Python was configured properly in the configure step of
    # the boost wscript (boost-python needs to be configured in the boost repo)
    if not bld.env['BUILD_PYTHON']:
        bld.fatal('Python was not configured properly')

    bld.load("wurf_common_tools")

    bld.env.append_unique(
        'DEFINES_STEINWURF_VERSION',
        'STEINWURF_PETRO_PYTHON_VERSION="{}"'.format(
            VERSION))

    # Remove NDEBUG which is added from conf.check_python_headers
    flag_to_remove = 'NDEBUG'
    defines = ['DEFINES_PYEMBED', 'DEFINES_PYEXT']
    for define in defines:
        while(flag_to_remove in bld.env[define]):
            bld.env[define].remove(flag_to_remove)

    bld.env['CFLAGS_PYEXT'] = []
    bld.env['CXXFLAGS_PYEXT'] = []

    CXX = bld.env.get_flat("CXX")
    # Matches both /usr/bin/g++ and /user/bin/clang++
    if 'g++' in CXX or 'clang' in CXX:
        bld.env.append_value('CXXFLAGS', '-fPIC')

    bld.recurse('src/petro_python')

    if bld.is_toplevel():
        if bld.has_tool_option('run_tests'):
            bld.add_post_fun(exec_test_python)


def exec_test_python(bld):
    python = bld.env['PYTHON'][0]
    env = dict(os.environ)
    env['PYTHONPATH'] = os.path.join(bld.out_dir, 'src', 'petro_python')

    # First, run the unit tests in the 'test' folder
    if os.path.exists('test'):
        for f in sorted(os.listdir('test')):
            if f.endswith('.py'):
                test = os.path.join('test', f)
                bld.cmd_and_log('{0} {1}\n'.format(python, test), env=env)

    # Then run the examples in the 'examples' folder
    if os.path.exists('examples'):
        for f in sorted(os.listdir('examples')):
            if f.endswith('.py'):
                example = os.path.join('examples', f)
                bld.cmd_and_log(
                    '{0} {1} --dry-run\n'.format(python, example), env=env)
