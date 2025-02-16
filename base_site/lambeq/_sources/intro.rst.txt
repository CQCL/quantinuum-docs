What is lambeq?
===============

``lambeq`` is an open-source, modular, extensible high-level Python library for experimental :term:`Quantum Natural Language Processing <quantum NLP (QNLP)>` (QNLP), created by `Quantinuum <https://www.quantinuum.com>`_'s QNLP team. At a high level, the library allows the conversion of any sentence to a :term:`quantum circuit`, based on a given :term:`compositional model` and certain parameterisation and choices of :term:`ansätze <ansatz (plural: ansätze)>`, and facilitates :ref:`training <sec-training>` for both quantum and classical NLP experiments. The notes for the latest release can be found :ref:`here <sec-release-notes>`.

``lambeq`` is available for Python 3.10 and higher, on Linux, macOS and Windows. To install, type:

.. code-block:: bash

   pip install lambeq

or refer to :ref:`sec-installation` for more information. To start the tutorial, go to :ref:`sec-sent_input`. To see the example notebooks, go to :ref:`sec-examples`. To use the command-line interface, read :ref:`sec-cli`. To make your own contributions to ``lambeq``, see :ref:`sec-contributing`.

Licence
-------

Licensed under the `Apache 2.0 License <http://www.apache.org/licenses/LICENSE-2.0>`_.

User support
------------

If you need help with ``lambeq`` or you think you have found a bug, please send an email to lambeq-support@quantinuum.com. You can also open an issue at ``lambeq``'s `GitHub repository <https://github.com/CQCL/lambeq>`_. Someone from the development team will respond to you as soon as possible. Furthermore, if you want to subscribe to ``lambeq``'s mailing list (lambeq-users@quantinuum.com), send an email to lambeq-support@quantinuum.com to let us know.

Note that the best way to get in touch with the QNLP community and learn about ``lambeq`` is to join our `QNLP discord server <https://discord.gg/TA63zghMrC>`_, where you can ask questions, get notified about important announcements and news, and chat with other QNLP researchers.

How to cite
-----------
If you use ``lambeq`` for your research, please cite the accompanying paper :cite:p:`kartsaklis_2021`:

.. code-block:: bash

   @article{kartsaklis2021lambeq,
      title={lambeq: {A}n {E}fficient {H}igh-{L}evel {P}ython {L}ibrary for {Q}uantum {NLP}},
      author={Dimitri Kartsaklis and Ian Fan and Richie Yeung and Anna Pearson and Robin Lorenz and Alexis Toumi and Giovanni de Felice and Konstantinos Meichanetzidis and Stephen Clark and Bob Coecke},
      year={2021},
      journal={arXiv preprint arXiv:2110.04236},
   }
