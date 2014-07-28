Introduction
============


Cron
====

You have to create a daily cron to check digests to produce

0 4 * * *   wget --http-user=zopescheduler --http-password=TrigOtad3 http://localhost:8080/mysite/@@digest-cron?maildigest-debug-mode=1 -O /dev/null

Manually check
==============

http://localhost:9880/mysite/@@digest-cron -O /dev/null


Tests
=====

This add-on is tested using Travis CI. The current status of the add-on is :

.. image:: https://secure.travis-ci.org/tdesvenain/collective.maildigest.png
    :target: http://travis-ci.org/tdesvenain/collective.maildigest

.. image:: https://coveralls.io/repos/tdesvenain/collective.maildigest/badge.png?branch=master
    :target: https://coveralls.io/r/tdesvenain/collective.maildigest?branch=master

