Useful commands
===============

Below are some fcm commands and tips I have found useful.

Getting your own local copy of CATNIP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

To create a branch off the CATNIP trunk::

    git branch [branch name]


The above command will create the new branch and sets it as your working branch noted by a '*' next to it. You can check this by using this command::

    git branch

output::

      master
    * branch name


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

**NEW GITHUB RELEVANT INSTRUCTIONS TO BE ADDED**
e.g. how to make a pull request

QA instructions for the reviewer
================================


Check out the function to be reviewed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**NEW GITHUB RELEVANT INSTRUCTIONS TO BE ADDED**

e.g. how to respond to a pull-request

Carry out a code review
^^^^^^^^^^^^^^^^^^^^^^^
**NEED TO DECIDE HOW MUCH OF THE INSTRUCTIONS HERE ARE STILL RELEVANT!**

To begin, create a new CodeReview wiki page. To do this go to the ticket for function to be reviewed. Modify ticket the description by adding: **[wiki:ticket/[ticketnumber]/CodeReview CodeReview]**

In the ticket description there should now be a 'CodeReview?' link. Click on this and from a drop down menu of templates choose CodeReview. Save any changes, the page has now been created.  `Example Code Review wiki <http://fcm1/projects/ciid/wiki/ticket/43/CodeReviewDewpoint43>`_

Test and review the code, for guidance, see Test and review the code, for guidance, see `http://www-nwp/~appsci/QA/code/guidance.shtml <http://www-nwp/~appsci/QA/code/guidance.shtml>`_

Also bear in mind that ideally all functions will:

* Compatible with Python 2 and 3 (you can use a tool like `2to3 <https://docs.python.org/2/library/2to3.html>`_ to check this.)
* Follow `pep8 <https://www.python.org/dev/peps/pep-0008/>`_ type style guidelines 
* Include a docstring that follows either `numpy or google <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_ docstring style. 
* Include a doctest.

Go back and forth with the code writer until you are both happy with the function
