# forsetiVisual
[WIP] Visualisation for forseti in GCP


If you happen to use Forseti and want to have a decent visualisation then this might help you. This is still work in progress and PRs will be appreciated. 
This will pull data from Google's Security Command Center convert from GRPC to JSON and push it into elasticsearch. 

You would need to have the below ENVs in your bash profile



```
export ORG_ID=1223334444
export PROJECT_ID=[YOUR PROJECTID]
export SERVICE_ACCOUNT=YOUR_SERVICE_ACCOUNT_NAME@project-id.iam.gserviceaccount.com
export KEY_LOCATION=~/project-id-fb3ejbq38f7be.json
export GOOGLE_APPLICATION_CREDENTIALS=$KEY_LOCATION

```
