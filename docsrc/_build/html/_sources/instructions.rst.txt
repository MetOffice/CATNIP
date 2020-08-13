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
needs to fix a bug or add new features without affecting the current working code.

To create a branch off the CATNIP master branch, make sure you are in the checked out directory of your repository,e.g.
*cd ~/CATNIP* then in case you already have another branch:

First make sure you are in the master branch and run::

    git checkout master

Then create your branch by running this command::

    git branch [branch name]


The above command will create the new branch and sets it as your working branch noted by a '*' next to it. You can check this by using this command::

    git branch

output::

      master

    * [branch name]


Add your function to the branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add your function to your branch and develop it. To add your function (from the directory where the working copy of your branch lives)::

    git add [file name]

To commit changes to the branch::

    git commit -m 'some description for your function'

**Note:** More information on git can be found here: https://git-scm.com/doc


Pushing your changes to the remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
you can push your branch to the remote github repository using this command::

    git push -u origin [branch name]


Passing the function to the reviewer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To tell others about the changes that you have pushed to a branch you make a pull request. This would allow for your
changes be discussed by the collaborators and any further changes be discussed. More details here:
https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request

Check out the branch to be reviewed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sometimes to do a review you need to actually work from someone else's branch. To do this we first need to fetch the
remote branches so that we have access to them locally. Make sure you are in the checked out directory,
e.g. *cd ~/CATNIP*, then run the following command::

    git fetch origin

Next we check out the branch we want::

    git checkout -b [remote_branch_name] origin/[remote_branch_name]


In later versions of git is simpler::

    git fetch
    gti checkout [remote_branch_name]

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


