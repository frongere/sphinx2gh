#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""A python command line tool to automate building and deployment of Sphinx documentation on GitHub static pages"""

from subprocess import call
import os
from distutils.dir_util import copy_tree, remove_tree
from tempfile import mkdtemp
from datetime import datetime
import argparse
from git import Repo

import sys

__year__ = datetime.now().year

__author__ = "Francois Rongere"
__copyright__ = "Copyright 2016-%u, Ecole Centrale de Nantes" % __year__
__credits__ = "Francois Rongere"
__licence__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Francois Rongere"
__email__ = "franrongere@gmail.com"
__status__ = "Development"

__all__ = ['main']


def get_current_branch(repo):
    branches = repo.git.branch()
    for branch in branches.split('\n'):
        if branch.startswith('*'):
            cur_branch = branch[2:]
            break
    return cur_branch


def checkout_branch(repo, branch):
    # TODO: faire le check que la branche demandee existe bien dans le repo
    print "\nChecking out to branch %s" % branch
    try:
        print repo.git.checkout(branch)
    except:
        raise RuntimeError('Unable to checkout to branch %s' % branch)


def is_github_repo(s):
    return 'github.com' in s


def is_doc_folder(s):
    return os.path.isfile('conf.py')


# Building parser
# ------------------------------------------------

try:
    import argcomplete
    has_argcomplete = True
except:
    has_argcomplete = False


parser = argparse.ArgumentParser(
    description=""" -- SPHINX2GH --
    
    A command line tool to automation the deployment of Sphinx documentation
    to GiHub static pages.
    """,
    epilog='-- Copyright 2016-%u  -- BSD --\n  Francois Rongere' % __year__,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument('repo', type=str, help="""path or url to the repo""")
parser.add_argument('--remote-gh', type=str, help="""The remote GitHub repository""")
parser.add_argument('--build-branch', type=str, help="The branch where we want to build documentation")
parser.add_argument('--doc-src', type=str, help="The folder where the documentation located")
parser.add_argument('--commit-msg', type=str, help="The commit message in gh-pages branch")


def main():
    
    if has_argcomplete:
        argcomplete.autocomplete(parser)
    
    args, unknown = parser.parse_known_args()
    
    print("\n=====================================================")
    print("Building and Deploying Sphinx documentation on GitHub")
    print("=====================================================\n")
    
    # Build temp folder to clone the repo
    working_dir = mkdtemp(suffix='_doc')
    
    print "\t--> Cloning the repository in %s" % working_dir
    repo = Repo.clone_from(args.repo, working_dir)
    os.chdir(working_dir)
    
    # TODO: check here if the gh-pages branch does exist
    
    cur_branch = get_current_branch(repo)
    
    # Setting the build branch
    if args.build_branch is None:
        # We consider it is the current branch
        build_branch = cur_branch
    else:
        # TODO: check if args.build_branch does exist
        build_branch = args.build_branch
    
    print "\n\t* Documentation wil be built on branch %s" % build_branch

    # Setting the remote GitHub repository
    if args.remote_gh is not None:
        try:
            assert is_github_repo(args.remote_gh)
        except AssertionError:
            raise AssertionError('%s is not a gitHub repository' % args.remote_gh)
        remote_gh = args.remote_gh

    else:
        if is_github_repo(args.repo):
            remote_gh = args.repo
        else:
            raise Exception('As the source repo is not a GitHub repo, you have to provide a remote GitHub with '
                            'the --remote-gh option')
    repo.git.remote('add', 'github', remote_gh)
    print "\n\t* Documentation will be pushed on the GitHub repo with url %s" % remote_gh
    
    
    # Setting the documentation folder
    doc_folder_guess = ['docs', 'doc', 'documentation']
    if args.doc_src is None:
        for doc_folder in doc_folder_guess:
            try:
                os.chdir(doc_folder)
                doc_src = os.getcwd()
                break
            except OSError:
                pass
        else:
            raise Exception('Tried to guess the doc folder but failed. Please provide it by the --doc-src option')
    
    else:
        try:
            assert os.path.isdir(args.doc_src)
            doc_src = args.doc_src
        except AssertionError:
            raise OSError('%s is not a valid doc folder' % args.doc_src)
        os.chdir(args.doc_src)
    
    try:
        assert is_doc_folder(doc_src)
    except AssertionError:
        raise AssertionError('%s is not a valid sphinx documentation folder' % doc_src)
    print "\n\t* The documentation foder is %s" % doc_src
    
    # Checking out the build branch
    build_sha = repo.git.log(n='1', pretty="format:%H")
    print "\n\t--> Checking out to build branch %s" % build_branch
    checkout_branch(repo, build_branch)
    # repo.git.pull(args.repo, build_branch)
    
    
    # Building the documentation
    print "\n\t--> Building the sphinx HTML documentation"
    try:
        call(['make', 'clean'])
        call(['make', 'html'])
    except:
        raise Exception('Unable to build the documentation')
    
    # Copying the HTML files to a temp dir
    html_dir = mkdtemp(suffix='_html')
    # TODO: recuperer le repertoire de build
    print "\n\t--> Copying HTML files to %s" % html_dir
    copy_tree(os.path.join(doc_src, '.build/html'), html_dir)
    
    print "\n\t--> Cleaning the working copy"
    call(['make', 'clean'])
    os.chdir('..')
    
    print "\n\t--> Checking out to branch gh-pages"
    
    # repo.git.pull(args.repo, 'gh-pages')
    checkout_branch(repo, 'gh-pages')
    
    call(['ls'])
    # TODO: trouver ici le moyen de tout effecer sauf les .git, .idea etc...
    # last_sha = repo.git.log(n='1', pretty="format:%H")
    # print "\n\t--> Removing last commited HTML files of revision %s" % last_sha
    # commited_files = repo.git.diff_tree(no_commit_id=True, name_only=True, r=last_sha).split('\n')
    # for commited_file in commited_files:
    #     try:
    #         print 'Deleting file %s' % commited_file
    #         os.remove(commited_file)
    #     except OSError:
    #         pass
    call(['rm', '-rf'])
    
    
    
    
    print "\n\t--> Copying back HTML files from %s to %s" % (html_dir, working_dir)
    copy_tree(html_dir, working_dir)
    
    
    print "\n\t--> Commiting new documentation"
    if args.commit_msg is None:
        msg = "Documentation update from rev %s on branch %s" % (build_sha, build_branch)
    else:
        msg = args.commit_msg
    
    sys.exit(0)
    repo.git.add('.', all=True)
    print repo.git.commit(m=msg)
    
    
    sys.exit(0)
    print "\n\t--> Pushing new revision to %s" % remote_gh
    repo.git.push('github', 'gh-pages')

    print "\n\t--> Cleaning temp folders"
    os.chdir('..')
    remove_tree(html_dir)
    remove_tree(working_dir)
    

if __name__ == '__main__':
    main()
