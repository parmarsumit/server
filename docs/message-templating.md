
## simple messages

ACTOR
(the actor of the event)

TARGET
(the actor targeted by the message)

ORIGIN
(the event itself)

ROOT
(the root of the structure, mainly the project)

ITEM
(the related item, ex: a contribution, a project, an initiative, etc ...)

PARENT
(the related ITEM parent. Ex: the intiative for a contribution)
)


## email contents

To display the url:

    {{url}}

To access the actor infos:

    {{actor.get_data.title}}
    {{actor.get_data.username}}

To obtain a link to the actor profile:

    {{actor.get_url}}

To access the item (contribution) data:

    {{node.get_data.title}}
    {{node.get_data.description}}
    {{node.get_data.value}}

To obtain a link to the item:

    {{node.get_url}}


To access the project data:

    {{node.get_root.get_data.title}}
    {{node.get_root.get_data.symbol}}
    {{node.get_root.get_data.description}}

To obtain a link to the project:

    {{node.get_root.get_url}}
