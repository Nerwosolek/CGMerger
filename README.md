# CGMerger
CodinGame Merger (merges files from a folder into one file served by ``CodinGame``
 web plugin)

## Installation

1. Make sure before that you have ``python3`` installed (at least version ``3.5``)
2. Run ``pip install cgmerger``
3. (alternative for 2.) You can also install it by downloading the package from 
 ``github`` and running ``pip install <folder where CGMerger is located>``

## Running the script

After installation, the script can be run by simply typing ``cgmerger`` command from
 the project folder that you use for ``CodinGame``.
 
## Example/Template project

Because the tool setup is not trivial, I've created a couple of sample projects that
should help anyone out with starting with the project. Simply copy the example folder
from those languages and you should be able to use the script:

- ``C#`` sample project: https://github.com/ajakubo1/CGmerger-examples/tree/main/default-csharp
- ``python`` sample project: https://github.com/ajakubo1/CGmerger-examples/tree/main/default-python

Please - share your successful setup of the script by opening a PR to https://github.com/ajakubo1/CGmerger-examples/

## How to use it automatically with IDE?

I use the script with ``PyCharm``. I define a new file watcher that is using 
``cgmerger`` command. It works perfectly for the ``python`` env.

## How does it all work?

The script works in general as follows:
1. It searches all of the files in folder specified by ``--workdir`` argument (by
 default, that folder is ``codingame``)
2. It takes all of the file names from that folder, filtered by ``--file-regex`` 
argument (by default ``.*`` - every file in ``workdir`` folder). It 
**does not** search folders in ``workdir`` folder.
3. It copies the contents of all of the found files, excluding lines matched by 
``--exclude-line-regex`` into single ``--output`` file in directory where the script
 runs (by default the file is named ``codingame.volatile.py``)

The script **does not** create any folders and files on it's own. It checks if
``--output`` file exists and informs the user if it doesn't (same thing for
``--workdir``). This is as intended - I do not want to mess with project file
structure, I only touch files that actually exist.

## Writing a config file

You can write your own config file for a project. In the beginning of the run, the
script will search for ``cgmerger.conf`` file and reads the configuration from it. 
You can still override the values provided by that script by specifying arguments
in command line.
  
Instead of writing your own ``cgmerger.conf``, you can simply run the 
``cgmerger --write`` command. This will create a ``cgmerger.conf`` from currently
loaded (probably default) settings. Next time you run the script, you don't have to
specify any arguments in the command line, settings from that file will be loaded.

For examples of config file, refer to https://github.com/ajakubo1/CGmerger-examples
project (you will find there example settings for a ``C#`` and ``python``)

## Parameters

If you want to know more about parameters, you can issue ``--help`` command. More
 explanations on each of the options:

For re-adjusting the script for different languages, you probably need to re-adjust
 those settings parameters:
- ``output`` - the default is a ``.py`` file, you should change it to something more
  aligned with the language used
- ``comment`` - this is the comment character (or characters) used in
 the language (e.g. ``#`` in ``python``, ``//`` in ``C#``). It is
 obligatory to set it unless project uses ``python``. This value is used to create
 nice separators in ``output`` file. 
- ``exclude_line_regex`` (**optional**) - this is regex used when script starts to
 copy file contents line-by-line to exclude some of the unneeded lines. E.g. in 
 ``.cs`` scripts lines starting with "using" should probably be excluded. 
 This can be done by setting ``exclude_line_regex`` to ``^using``.
- ``header`` (**optional**) - file located relatively to ``workdir`` folder that will be
  copied before any other file in the ``workdir``. It is ignored by ``file_regex`` 
  setting. The contents of this file are not filetered by ``exclude_line_regex`` 
  setting.
- ``footer`` (**optional**) - file located relatively to ``workdir`` that will
  be copied after any other file in the ``workdir`` (the last file added to ``output``). 
  It is ignored by ``file_regex`` setting.
- ``order`` (**optional**) - List of files separated by comma, specified in order of
 which they should be copied to the ``output``. Example: ``one.cs,two.cs,three.cs``. 
 ``output`` files will be added right after the ``header`` file (if it was specified). 
 If any of the listed files are in ``header`` or ``footer`` - they will not be 
 duplicated and its contents  will be ignored (``header`` file and ``footer`` file has 
 higher priority than ``order``). After all of the files from ``order`` are copied, 
 the script will copy the rest of the files according to ``file_regex``. ``order`` files 
 themselves are not checked with ``file_regex``.
- ``file_regex`` (**optional**) - this is regex used to define which files from
 ``workdir`` should be copied to ``output`` file. By default, the command will
 copy the contents of all of the files in that folder. You can change it to target
 different file types (e.g. ``.*.cs`` files instead of ``.*.py`` files)
