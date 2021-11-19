# Contributor workflow

Creating a high-level pattern library like this one comes with risks. The most significant one is premature abstraction. Our general approach here is that API design happens best in the context of real-world applications. Features should be proposed for this library once they have reached a certain level of stability.

We don't want to have an excessively prescriptive sense of what is 'in' and 'out' of scope for this library. So long as something fits within our architecture, is testable, and has an API that has stabilised through real-world use, it's a candidate for inclusion.

## New features and functionality

1. The first stage of adding a new module happens within an application that uses it. Use the convention of placing it in the `commonknowledge.experimental` package within your application repository to indicate to other people that it's in the process of being abstracted and that they should be mindful of these guidelines.
2. Remove any dependencies from application code outside the `commonknowledge` package. Start to think about how it can be tested in isolation (if it isn't already).
3. Open a feature request against this repository. Describe the new feature, include links to your implementation other repositories. If the application is publicly accessible, include links to it in the live app.
4. Discuss and refine the API with other contributors.
5. When the feature request is accepted, fork this repository (or create a feature branch if you have write access), and commit the feature implementation. Ensure that you have good test coverage of both python and javascript components and all public API methods are documented.

## Bugs & backward-compatible API changes

We're more open to backward-compatible API changes. For smaller changes, opening a pull request is fine.

Some additional pointers:

- Ensure that you have good test coverage of both python and javascript components and all public API methods are documented.
- These changes are always a good opportuntiy to improve test coverage of the exsting functionality. Think about how your changes may lead to regressions to the existing functionality and add tests to guard against them.


## Improvements to documentation

Yes please!
