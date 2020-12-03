Useful commands
===============

Below are some useful git commands and tips.

Getting your own local copy of CATNIP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

CATNIP is a Metoffice/Private repository. You must have a github account with at least a *Read* access. You can get
a local copy of the CATNIP library by cloning it either

via SSH::

    git clone git@github.com:MetOffice/CATNIP.git


**Note:** make sure you you SSH key is linked to your github account. More information can be found in here:
https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh

or via HTTPS::

    git clone https://github.com/MetOffice/CATNIP.git

Doctest in brief
^^^^^^^^^^^^^^^^

Doc tests are a simple but useful way of checking your function does what you are expecting it to do. The doctest module along with examples is described `here <https://docs.python.org/2/library/doctest.html>`_

Essentially, doctest looks through your code for text that has the format of an interactive python session. It executes that text as python code to check that it works exactly as shown. Below is a very simple example of a function which includes a doc test::

    """
    doctest example called example.py
    """

    def add_one(x): 
        """
        This function adds 1.0 to a number.
        Below is a doctest:

        >>> x = 12
        >>> y = add_one(x)
        >>> print(y)
        13.0
        """
    
        y = x + 1.
        return y

    if __name__ == "__main__":
        import doctest
        doctest.testmod()

To check that our function is working as expected, and passes the doctest we can simply::

    python example.py

If the tests are successful, nothing will be returned, for a verbose response use::

    python example.py -v
    Trying:
        x = 12
    Expecting nothing
    ok
    Trying:
        y = add_one(x)
    Expecting nothing
    ok
    Trying:
        print(y)
    Expecting:
        13.0
    ok
    1 items had no tests:
        __main__
    1 items passed all tests:
       3 tests in __main__.add_one
    3 tests in 2 items.
    3 passed and 0 failed.
    Test passed.

All CATNIP tools should have a doctest, it can also be useful to include doc tests to check your function reports the expected error messages when it fails.

QA instructions for the function writer
=======================================

Open an issue
^^^^^^^^^^^^^

Open a ticket on https://github.com/MetOffice/CATNIP/issues and describe the function.

Create a branch
^^^^^^^^^^^^^^^

In Git, creating a branch is a way to start a separate line of development. This is usually done when a developer
needs to fix a bug or add new features without affecting the current working code. The branching method varies depending on the type of workflow  you
have chosen for CATNIP we are using the Gitflow workflow. More details can be found here:
https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow

This workflow uses two branches to record the history of the project. A *master* branch to store the stable version of the project
and a *develop* branch to serve for adding new features. CATNIP already has a *develop* so you only need to check it out, make sure you
are in the checked out directory of your repository,e.g.
*cd ~/CATNIP* then in case you already have another branch:

First make sure you are in the master branch and run::

    git checkout master

Then checkout the *develop* branch by running this command::

    git checkout develop


The above command will create a local *develop* branch and sets it as your working branch noted by a '*' next to it. You can check this by using this command::

    git branch

output::

      master

    * develop


Add your feature to the branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Before you add a new feature to the project you need to create a *feature_branch* by running the following commands::

    git checkout develop
    git checkout -b [feature_branch]

**Note:** it is a good idea to name your feature branch in a way that is easily identifiable and ideally linked to an already existing
github issue, e.g. *feature_adding_new_doctest_i123*

Once you have done your changes to add them to the *feature_branch* make sure you are in the *feature_branch* by running the following commands ::

    git checkout [feature_branch]
    git add [new/modified file name]

To commit your changes to the *[feature_branch]*::

    git commit -m 'some description for your changes'

**Note:** More information on git can be found here: https://git-scm.com/doc

Pushing your changes to the remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
you can push your *[feature_branch]* into the remote *develop* github repository by running this command::

    git push -u origin [feature_branch_name]


Passing the function to the reviewer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To tell others about the changes that you have pushed to a branch you make a pull request. This would allow for your
changes be discussed by the collaborators and any further changes be discussed. More details here:
https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request

Check out the branch to be reviewed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes to do a review we need to actually work from an already existing branch. To do this we first need to fetch the
remote branches so that we have access to them locally. Make sure you are in the checked out directory and the *develop* branch,
e.g. *cd ~/CATNIP*, then run the following command::

    git checkout develop
    git fetch

This will list all the branches created off the *develop* branchd. Next we check out the branch we want::

    gti checkout [remote_branch_name]

We can now make our changes and follow the same process as described for the *feature_branch* above.

Merging into develop/master branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Once a pull request for a *feature_branch* is approved the branch can be merged and the local copy deleted. In CATNIP the merging
into *develop* and *master* branches are done by the admin team. Once a *feature_branch* is merged it can be deleted locally by
running the following command::

    git checkout develop
    git branch -d [feature_branch_name]

QA instructions for the reviewer
================================
Things to consider:
    - Can I run the code without error
    - Are the associated tests, e.g. docstring tests pass successfully (run the script with -v option to see result of the doctest)
    - Are you satisfied the change set fulfils the requirement set out in the ticket?
    - Are you happy that the change does not cause any undesirable side effects?
    - Is the documentation for this change sufficient, accurate, and understandable?
    - Are there impacts on existing functionality?

Also bear in mind that ideally all functions will:
    - Compatible with Python 2 and 3 (you can use `2to3 <https://docs.python.org/2/library/2to3.html>`_.
    - Follow the `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ styling guidelines. We recommend `Flake8 <https://pypi.org/project/flake8/>`_ as one of the tools for enforcing PEP8 guidelines.
    - Include a docstring that follows either `numpy or google <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_ docstring style.
    - Go back and forth with the code writer until you are both happy with the function.

Some Git best practices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Use branches
- Name the branches with appropriate prefixes
- Commit related changes
- Commit often
- Don't commit unfinished work
- Test before you commit
- Write useful commit messages

For more details see Git Commit Best Practices `Page <https://github.com/trein/dev-best-practices/wiki/Git-Commit-Best-Practices>`_


