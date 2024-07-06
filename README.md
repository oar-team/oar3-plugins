# oar-plugins

This project contains the official oar plugins.
It is also a good place to start if you want to create your own plugin repository.

**The documentation to install, and write oar3 plugins is available ([here](https://oar-3.readthedocs.io/en/latest/admin/extensions.html)).**

# Getting Started

To get started with your own plugin development:

You need the following dependencies:

- python3
- [libpq](https://www.postgresql.org/docs/15/index.html) (needed for [psycopg2](https://www.psycopg.org/docs/install.html))


On debian the following command is sufficient (tested on ):

```bash
sudo apt install libpq-dev
```

Install the plugin to run the test locally:

```bash
# Clone the repo (or fork if you prefer)
git clone https://github.com/oar-team/oar3-plugins

cd oar3-plugins

# We use poetry install the dependencies
pip install poetry

# Install the dependencies
poetry install

# Dive into a shell containing the newly installed dependencies
poetry shell

# Execute the tests
pytest tests
```

Now that you are able to run the tests you can start developing your own plugins.
For more information about running OAR, and testing your plugin with an OAR installation please refer to 
the official OAR [documentation](https://oar-3.readthedocs.io/en/latest/) (and  [the page dedicated to plugins ](https://oar-3.readthedocs.io/en/latest/admin/extensions.html)).
