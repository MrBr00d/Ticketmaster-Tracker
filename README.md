# Ticketmaster tracker

This app is a tracker for ticketmaster. It scrapes ticketmaster based on user defined concerts,
and sends a push notification using the [ntfy](https://ntfy.sh/) platform.

# Considerations
This flask app should be served using nginx/apache, this is not included in the repo.
You should start a guicorn instance with workers and point to the socket.

Also, the entire app considers /tmt as a location for the website. In order to use a different one you should modify the routes in flask.
Also also, the static files should be in a folder with the same name as the location. e.g. /tmt/static
