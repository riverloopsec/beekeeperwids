


# brainstorming the implementation of a simple, snort-like rule language
# this might be a good place to start and then expand into a bro-like comprehensive language
# this is fun :)



rule syntax:

rule data : condition(s) : actions(s)


actions are drawn from existing eventPlugins, conditions are drawn from analyticPlugins


there will be a set of core plugins, but users can add their own plugins

when an App runs, it will load and launch the plugins which will generate events, and
then it will monitor to see if the events match the loaded rules



alert.email('email@email.com'), alert.log('myfile.log') : packet.










