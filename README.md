Levitan
=======

Skype bot for development teams. 


##About

Levitan was our internal tool to share information about builds, environment usage and releases.

It was intended to do the following things:

* Inform about taking and freeing environments
* Inform about passing builds from Jenkins
* Inform about Jenkins jobs statuses and versions

We are trying to recreate Levitan as an open-source and *extensible* project.
 
 
## How does it work? 

Levitan constists of two core components: socket listening module and Skype module. The last one is the most important. When you start Levitan, it connects to your current Skype session and starts responding commands from others. 

Responding to commands depends on plugins. We have some examples here, which we are using in our team. Most of plugins are intended to run in chat rooms, not individual chats (like EnvPlugin), so one Levitan instance can manage different teams. 

The other part is responding to data, coming from socket listener. It's called Socket Feature and described below.

We recommend creating a separate account for Levitan and running it separartely. For instance, you can create Docker image with X11 on remote serever and run it from there. 

Levitan itself and its plugins are configured via `levitan.conf` file formatted as JSON. [Here](https://github.com/Sicness/levitan/wiki/Configuration) you can find more information on configuring Levitan or you can just check `levitan.conf.example`. 


###Socket Feature

Levitan features are mainly described by used plugins. However, one built-in option is available
disregarding its addons.

When Levitan is started, it begins to listen to defined `bind:port` in configuration section. So, you can send requests
via, for example `nc` formatted as `echo '{"room":"roomKey", "message":"Your Message"}' | nc bind port`.

`roomKey` is the key for your rooms, defined in `rooms` section in configuration file like here:
`{"team1" : "Levitan2 Test"}`


###Plugins

Plugin is a module added on startup, basing on configuration, which responds to some messages, chosen by regexps. 

In this repository you will find following plugins:

* [HiPlugin](https://github.com/Sicness/levitan/wiki/HiPlugin)
* [JenkinsJob](https://github.com/Sicness/levitan/wiki/JenkinsJob)
* [EnvPlugin](https://github.com/Sicness/levitan/wiki/EnvPlugin)

Notes on plugin usage and creation can be found in the [project wiki](https://github.com/Sicness/levitan/wiki).


##Dependencies

* Python 2.7
* [awahlig/skype4py](https://github.com/awahlig/skype4py)
