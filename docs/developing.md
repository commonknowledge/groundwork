# Developing

## Easy mode: Development containers

We love development containers. They keep your development environment in a VM and isolated from the rest of your device which is good security practice. They also make it extremely easy to share editor configurations and development dependencies that can't be managed using language package managers.

Much as we hate to stan Microsoft, it's the easiest option to work on this library.

### In Visual Studio Code

1. From the command palette select "Remote Containers: Clone Repository in Named Container Volume".
* Enter: `git@github.com:commonknowledge/pycommonknowledge.git`.
* Choose a development container to install to, or create a new one.
* Wait for the container to initialize and the project bootstrap scripts to finish.


### More information

- [VSCode Development Containers](https://code.visualstudio.com/docs/remote/containers)


## Hard mode: Do it yourself

1. Ensure that you have the following installed:
    - NodeJS
    - Yarn
    - Python 3.9+
    - Poetry
    
* Follow the installation instructions for [DjangoGIS's local dependencies](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/install/postgis/).
* Ensure that you have the `DATABASE_URL` environmental variable pointing to a local postgres database.
* Clone the repository and run `make bootstrap`.
