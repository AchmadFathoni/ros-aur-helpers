import sys
import argparse
import os
from aurci.bootstrap import Clone, Pull
from aurci.build import Packages
from aurci.update import Update
from aurci.general import Routines


def commands(option, package, verbosity, output):
    args = {
        "clone"  : (Clone, "clone"),
        "pull"   : (Pull, "pull"),
        "build"  : (Packages, "build"),
        "deploy" : (Packages, "deploy"),
        "update" : (Update, "update_pkgbuild")
    }
    command_class = args[option]
    getattr(command_class[0](package, verbosity, output), command_class[1])()


def main(argv):
    parser=argparse.ArgumentParser(prog='rosaur', add_help=True)
    exclu_group = parser.add_mutually_exclusive_group()

    parser.add_argument('command', choices=['clone', 'pull', 'build', 'deploy', 'update'])
    parser.add_argument('package', type=str)
    exclu_group.add_argument('-v', '--verbose', help='Increase verbosity', action="store_true")
    exclu_group.add_argument('-q', '--quiet', help='Suppress output', action="store_false")

    args = parser.parse_args(argv)

    def retry_with_rosdistro_name():
        name = "{0}{1}".format(Routines().get_ros_distro(), args.package)
        if os.path.exists(os.path.join(Routines.CACHE_ROOT, "packages/", name)):
            try:
                commands(args.command, name, args.verbose, args.quiet)
            except KeyError:
                print(f"Error: {args.package} could not be found in ROS Metainfo dict while running {args.command}")
            except FileNotFoundError:
                print(f"Error: {args.package} folder could not be found while running {args.command}")

    try:
        commands(args.command, args.package, args.verbose, args.quiet)
    except KeyError:
        retry_with_rosdistro_name()
    except FileNotFoundError:
        retry_with_rosdistro_name()

if __name__=='__main__':
    main(sys.argv)
