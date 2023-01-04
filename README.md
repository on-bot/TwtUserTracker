
# TwTUserTracker 🐦

Stands for TwitterUserTracker

As the Name describes it tracks users (yes users not user). Tracks not as in stalk hmm maybe stalk err it justs checks who they are following

Whenever the list of users who are stored in target follow someone, it sends a message letting you know who they followed (kinda useful right not creepy)



## Setup 🔧

### - config.json

- If you are running this locally you dont need to store the api keys on environment variables you can just store it on config.json and use the application. (You will need to tweak the code a little bit tho to get the keys from there)

### - MongoDB

- You will need to create an account on [MongoDB](https://www.mongodb.com/) and get an api key 
- If you are having a hard time to do this, you can find a tutorial in youtube or somewhere

### - Twitter

- Request a [Twitter Developer Account](https://developer.twitter.com/en/apply-for-access) (with [Elevated Access](https://developer.twitter.com/en/portal/products/elevated), then create a Twitter Developer App (make sure you change it to have both read/write permissions) (Also Not sure if Elevated Access is needed but its better)

### - Discord

- You will need a [discord app](https://discord.com/developers/applications) and its token (This is for the bot that you can use to add the list of targets that you want to track)
- Two [Webhooks](https://discord.com/developers/docs/resources/webhook) , One for Logging and One for the webhook that sends message (Notification)
