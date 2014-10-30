Levitan
=======

Skype bot for development teams. 


##About

Levitan was our internal tools to share information about builds, environments and releases.

It was intended to do the following things:

* Inform about taking and freeing environments
* Inform about passing builds from Jenkins
* Inform about Jenkins jobs statuses and versions

We are trying to recreate Levitan as an open-source and *extensible* project.

##NC Feature

Levitan features are mainly described by used plugins. However, one built-in option is available
disregarding its addons.

When Levitan is started, it begins to listen to defined `bind:port` in configuration section. So, you can send requests
via, for example `nc` formatted as `echo '{"room":"roomKey", "message":"Your Message"}' | nc bind port`.

`roomKey` is the key for your rooms, defined in `rooms` section in configuration file like here:
`{"test" : "Levitan2 Test"}`

Other features and plugin description can be found on [project wiki](https://github.com/Sicness/levitan/wiki).

##Dependencies

* Python 2.7
* [Skype4Py](https://github.com/awahlig/skype4py)

##Plugins

In this repository you will find following plugins:

* HiPlugin




