




# API

id + action = event

## a link for everything



### doing something to something


action -> reaction

from the payload to the event.

At first, the request must check for it's up to date status by collecting and applying the last events.

Once actor is authenticated by it's key, we obtain an identified context in witch action can be performed.

The actor must be related to an existing event.
The first step into creating the context is to check for an existing id, then creating it if not.

The actor is then authorized or not by checking for permissions.

Data is then pushed to input validation.
Once the action data is validated, requirements must be met.
If not, the request is sent to rendering.

When performing the action, one core event object is built from the context and the input data validated against.

If the validation fails, the response is rendered and returned with the input validation errors it faces.

Upon request completion, this can result in a authorization callback (as the login, as a contract call) where input data is stored and associated with the actor, waiting for callback to perform the action.

Otherwise, the created instance is saved and it's inferred roles and types are updated.

Then, the notification process collects actors involved by their rules on the new event and pushes notifications to them.
Webhook request associated with push notifications are then triggered in an asynchronous queue.

The request is finally rendered if needed with reference to the newly created event, the new origin for an action.

On the rendering step, by analyzing the event types and rules, we can update the actor application state, display them it's possible actions, redirect him to something else ...

This reflects a consistent state over the possible interactions. By waiting a transactional unlock, another process can stay sync and manage another request.

## Navigating in the data

That's the UI architecture that manages the user experience.

The server provides the necessary infrastructure to handle actions scenarios. As we see in redux, react we can stay consistent and enable the power of a great UX with the complementarity of a distributed application logic.

By splitting them, we enable user experience to be set according to the user needs while preserving commons on the underlying logic.

That's what does the blockchain with smart contracts and public access to transaction ledger, allowing the users of the network to share application logic and data, accessible by any interface.

ILOT aims at providing an accessibility layer in the very same nature.

The action semantics used to describe the application logic allows us to compile in many languages, use the logic to counterfit problems in changing the users ability to take control of what he needs. It enables non technical people to collect insights of what happens. It makes the rules much more clear and understandable.

If something sounds wrong, we can focus and discuss it without knowing code, as it's related to logic and semantic.

Actions semantics are made of algebra and semantics.
It's a matter of moving thing we define. Moving value from one cell to another, sharing a common language, counting and projecting things together.






## Interfaces

As the event have been saved and managed, this corresponds to a new uid accessible for actions.

The context that starts the action is the final uid.

All this process can be accessed using GET/POST but also PUSH/PULL on the websocket.

Interfaces defines entry points and can be used as namespaces.

They bound the gap between the served application, namespace and UI.

I'm sure we can also make a move to fit REST api systems.

We can have the classic GET/POST, HEAD/PUT to disable rendering.
We can use DELETE to 'Undo' thing maybe ? cancel an authorization callback, etc ...




## rules on types


Types are based on status resulting from actions.
They are extending or overriding the types they are originated.

They are scoped to the event itself or the structural item it is related. It can also be a more "global" context.

When referring to the actor or target of the event, it defines roles.

In order to define witch action a user can perform on an event, we filter rules applying to the event inferred types, then filter by the actor roles on it.

It's an allow, disallow scheme.

The roles can be inherit from a hierarchic tree structure and extended by the user root context.
This allows us to give the project owners rights to the project structure to registred users.

This way we can handle event chains to enable user progression in action patterns.

They are gouped along with actions in packages.

As some concepts are "standards", we can have packages of functionalities unrestricted to a particular type, but operable on any element.


## What are infered types ?

The base model simply records what'is done by whom.

When you "createProject", the resulting event is a "createdProject".

From this, we can infer that the event object defines a Project.

The actor of the action performed is the ProjectCreator.

When we invite someone to this project, we will do "inviteSomeone" on a "Project".

So, we will call project_id/inviteSomeone?email=invited@domaine.com

The resulting event is an InvitationToProject, the target a InvitedUser ?




#

On the service, anything is addressable with it's id.

Actions you can perform on them are defined by rules witch allows agents to push data to infered typed.


# CQRS - Command and query responsability segregation

https://fr.slideshare.net/ericdecarufel/cqrs-event-sourcing-14812997

https://pyxis-studio.com/fr/cqrs-event-sourcing/



# event sourcing

https://blog.xebia.fr/2017/01/16/event-sourcing-comprendre-les-bases-dun-systeme-evenementiel/

https://eventuate.io/whyeventsourcing.html


# Domain-driven design (DDD)

https://blog.xebia.fr/2009/01/28/ddd-la-conception-qui-lie-le-fonctionnel-et-le-code/

https://en.wikipedia.org/wiki/Domain-driven_design


# action semantics
