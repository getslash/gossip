Sphinx Extension
================
Some packages depending on gossip use hooks as part of their public APIs. In such cases, adding hook information to their respective documentation pages may be needed.
Gossip supports doing just that through its sphinx extension. In order to use it, install gossip with `sphinx` extra:

#. Install gossip with `doc` extra:

   .. code-block:: none

       pip install 'gossip[doc]'

#. Add ``gossip.contrib.sphinx_ext`` to the `extensions` list in Sphinx configuration file
#. Use the extension by adding the following code to your one of your rst files:

   .. code-block:: none

      .. gossip::
        :group_name: requrested-group

