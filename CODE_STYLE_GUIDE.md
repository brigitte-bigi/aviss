# Code style guide

## General rules

### Base coding rules

The base rules are in PEP8 Style Guide: <https://peps.python.org/pep-0008/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.

### Commit message

A correct commit message must therefore be structured as:
`name.of.module: Action message`
where Action includes but is not limited to "added", "fixed", "cleaned", "removed".
Example: 
```
sppas.src.annotations.Cuedpseech.whenhend: Fixed test for the model 4 -- custom rules.
\n\nA long description is welcome explaining the reason(s) of these changes but
not the changes themselves.
```

### Naming

- General class names are in Pascal Case. Example: `class WorkerOnSomething:`.
- SPPAS integrated class names are in CamelCase. Example: `class sppasWorkerOnSomething:`
- Function names are Snake Cases: all words lowercase separated by underscores. Example `def work_hard():`
- Variable names and objects are Snake Cases: all words lowercase separated by underscores,
   and must express their use more than their type. Example `work_hard = True`. Exceptions: 
   local iterators variables like i, j, k.
- Constants are Upper Case with Underscores. Example: `MSG_HELLO = _("Hello")`.
- Files that define a class should have the same name as the class but in Snake Case;
   and it should contain only one class. Example: `worker_on_something.py`. Abbreviations are 
   allowed. Example: `worker_on_sth.py`.

### Formatting

- Special characters like page break must be avoided.
- Indentation must use 4 spaces everywhere.

### Commenting

Comments are in American English. 
Consider a comment to be like a sentence: it starts with an uppercase,
it contains a verb, and it explains something that is not obvious when reading the lines
of code. The sentences should be in the passive voice, so they do not use 'you' or 'we'.

There can never be too many comments in a program! However, tricky code should not be 
commented on but rewritten! In general, the use of comments should be minimized through
appropriate naming choices and an explicit logical structure.


### Documentation Strings

The base rules are in PEP257 Style Guide: <https://peps.python.org/pep-0257/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.

### Type Hints

The base rules are in PEP484 Style Guide: <https://peps.python.org/pep-0484/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.


## AudiooPy specific rules

### Coding rules

- Limit all lines to a maximum of 119 characters.
- Do not use in-line comments.
- For type hints, do not use 'typing' library.
- Do not use property decorator. Use "property" function instead.

- Always explicit what is compared to what. Do not use 'not'. Examples:
```python
>>> # Correct -- also because it makes everything clear:
>>> # if boolean
>>> if greeting is False:
>>>     pass
>>> # if int
>>> if greeting == 0:
>>>     pass
>>> # if string
>>> if greeting == '0':
>>>     pass
>>> # if None
>>> if greeting is None:
>>>     pass
>>> # if list, tuple or dict
>>> if len(greeting) == 0:
>>>    pass

>>> # Wrong because it's too confusing and can induce an error:
>>> if greeting: 
>>>    pass
>>> if not greeting:
>>>    pass
```

### Documentation Strings

- The short summary is limited to 79 characters. It starts with an uppercase and ends with a dot.
- Markdown syntax can be used but is limited to `markdown2` support.
- An extra blank-line must be added before closing.
- Notice that there's a space after 'param' but both 'return', 'raises' and 'example' are surrounded by ":".

Example:

```python
>>>def add(a: int, b: int) -> int:
>>>"""Return the sum of two integers.

   It checks the types of given parameters and return their sum if both are integers.
   
   :example:
   >>> add(3, 4)
   7
   >>> add(3, -4)
   -1
   >>> add('3', 4)
   TypeError("First parameter is not an int")
   
   :param a: (int) First value to be added
   :param b: (int) Second value to be added
   :raises: TypeError: First parameter is not an int
   :raises: TypeError: Second parameter is not an int
   :return: (int) The sum of the given parameters

   """
```

See ClammingPy for additional details and examples: <https://clamming.sourceforge.io/>.

### File headers

A file header contains **only** legal and metadata information:

```
"""
:filename: my_module.py
:author: Firstname Lastname
:contact: email@example.org
:summary: One-line summary of the file.

..
    Copyright notice and license text.
    This banner notice must not be removed.
    -------------------------------------------------------------------------

"""
```

**Rules:**

- No descriptive text after the legal block. No list of functions or classes.
- The `:summary:` line is a one-line title only (≤ 79 characters).
- Any description of what the module does belongs in the class docstring,
  not in the file header.

### Class docstrings

The class docstring is the primary documentation of a module. It must explain:

- What the class represents or does.
- The key design decisions or constraints (e.g. external tools used, ordering
  of operations).
- At least one `:example:` block showing typical usage.

Do not duplicate information already visible from method signatures.

### Package documentation (README.md)

Each Python package directory (`__init__.py`) must contain a `README.md` file.
Its purpose is to explain how the classes of the package articulate — something
that no individual class docstring can cover.

Contents of a package README:

- A short description of the package's role.
- A table listing each class and its one-line role.
- A workflow diagram or ordered list showing how the classes interact
  (data flow, call order, dependencies).

### Justification for Style Adaptations

The author of the SPPAS has a visual impairment, and these modifications 
to standard coding guidelines are aimed at enhancing code readability and 
accessibility.

While the general principles of PEP8, PEP257, and PEP484 are followed, 
certain adjustments are made to accommodate specific needs related to 
visual clarity, for example:

- Avoiding the 'typing' Library: The use of type hints from the 'typing' 
  library is deliberately avoided as they tend to clutter the code, making 
  declarations more difficult to read. By removing this layer of complexity,   
  the code remains clear and manageable, allowing for faster comprehension 
  and easier maintenance.
- Explicit Comparisons: The preference for explicit comparisons (e.g., if 
  greeting == 0: instead of if greeting:) is designed to minimize ambiguity.
  This makes the logical flow of the code more apparent, reducing the 
  cognitive load when navigating through conditions and comparisons.
- Line Length Limit: A line length of 119 characters is permitted, slightly 
  longer than PEP8’s recommendation of 79. This provides more flexibility, 
  reducing unnecessary line breaks while still maintaining readability on 
  modern wide-screen displays.

These adaptations are essential for maintaining efficient and **accessible**
coding practices while adhering to the general spirit of Python's style 
guidelines. 

> They ensure that the code remains functional and clean, while also 
  addressing the specific needs of developers with visual impairments.

