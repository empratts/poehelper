"""
API module interfaces with the pathofexile.com API's
    -Makes requests to the character/stash API's
    -Parses/stores API responses
    -Manages Rate limiting
    -Provides URL's of trade searches for items recommended by the character progression module
"""

import requests
import datetime

headers = {
    'User-Agent': 'PoEHelper/0.1 (+pratts.eric@gmail.com)'
}

class API:

    def __init__(self, settings):
        self.settings = settings
        self.stashTabURL = 'https://www.pathofexile.com/character-window/get-stash-items?league={}&tabs=1&tabIndex={}&accountName={}'
        self.stashTabAPI = 'https://www.pathofexile.com/character-window/get-stash-items'
        self.characterURL = 'https://www.pathofexile.com/character-window/get-items'
        self.characterAPI = 'https://www.pathofexile.com/character-window/get-items'
        self.rateLimit = RateLimiter()

    def updateStashTab(self, tabName):
        
        league = self.settings.currentSettings["league"]
        tabIndex = self.settings.currentSettings[tabName]["index"]
        account = self.settings.currentSettings["account"]
        POESESSID = self.settings.currentSettings["POESESSID"]
        tabName = self.settings.currentSettings[tabName]["tab"]

        stash = {}

        if self.rateLimit.checkRateLimit(self.stashTabAPI):
            cookies = {'POESESSID':POESESSID}
            url = self.stashTabURL.format(league, tabIndex, account)
            response = requests.get(url,headers=headers,cookies=cookies)
            print("GET: {}".format(url))

            if response.status_code != 200:
                print("HTTP Error: " + str(response.status_code))
                return None
            else:
                stash = response.json()

            self.rateLimit.processResponse(self.stashTabAPI, response.headers) #are these headers valid in non-200 status cases?
        #add code here to return a cached response if the rate limit is reached
        if stash != {}:
            for tab in stash["tabs"]:
                if tab["n"] == tabName:
                    if tab["i"] != tabIndex:
                        #the tab has moved in the stash. Update its index in the settings and request it at its new location.
                        tabIndex = tab["i"]
                        self.settings.updateWrappedSetting(tabName + ":index", tab["i"])
                        #Try to fetch the stash again at its new index
                        if self.rateLimit.checkRateLimit(self.stashTabAPI):
                            url = self.stashTabURL.format(league, tab["i"], account)
                            response = requests.get(url,headers=headers,cookies=cookies)
                            print("GET: {}".format(url))

                            if response.status_code != 200:
                                print("HTTP Error: " + str(response.status_code))
                                return None
                            else:
                                stash = response.json()

                            self.rateLimit.processResponse(self.stashTabAPI, response.headers) #are these headers valid in non-200 status cases?
                    break
        
        if stash != {}:
            windowSettings = self.settings.getWindowSettings(tabName)
            for tab in stash["tabs"]:
                if tab["n"] == tabName and tab["i"] == tabIndex and tab["type"] != windowSettings["tabType"]:
                    self.settings.updateWrappedSetting("#"+tabName+":tabType", tab["type"])
                    self.settings.writeSettings()
                    break
        return stash
       
    def updateCharacter(self):
        account = self.settings.currentSettings["account"]
        character = self.settings.currentSettings["character"]
        POESESSID = self.settings.currentSettings["POESESSID"]

        char = {}

        if self.rateLimit.checkRateLimit(self.characterAPI):
            cookies = {'POESESSID':POESESSID}
            data = {'accountName':account,'realm':'pc','character':character}
            url = self.characterURL

            response = requests.post(url, headers=headers, cookies=cookies, data=data) #if this errors, might need to change to using json instead of data
            print("POST: {}".format(url))

            if response.status_code != 200:
                print("HTTP Error: " + str(response.status_code))
                return None
            else:
                char = response.json()

            self.rateLimit.processResponse(self.characterAPI, response.headers) #are these headers valid in non-200 status cases?

        return char
    
    def tradeSearch(self, parameters):

        return

    def tradeItemFetch(self, ids):

        return

class RateLimiter:
    """ This module is built to monitor rate limits implemented by the pathofexile.com API. Their response headers have the following types of fields:
        x-rate-limit-account: 4:6:60
        x-rate-limit-account-state: 1:6:0
        x-rate-limit-ip: 10:6:60,12:12:60
        x-rate-limit-ip-state: 1:6:0,1:12:0
        x-rate-limit-policy: trade-search-request-limit
        x-rate-limit-rules: Account,Ip
        
        As far as I can tell, each policy rate limits independently, and not all policies have the same rules. Also, each rule can have more than 1 condition. In the above case, the IP rule has 2 conditions.
            One condition that allows 10 requests every 6 seconds with a 60 second timeout if you break it "10:6:60" (<limit>:<window>:<lockout>), and another condition that allows 12 requests in 12 seconds with a 60 second lockout "12:12:60".
            
            Update:
                The 4 second windows from the trade-fetch-request-limit policy on the trade API seem to fucntiond different than the 60+ second windows from the character-window/get-stash-items" API. It is possible that the 2 API's implement rate limiting
                using different methods. The trade API seems to keep a live, running count of the number of requests make in the last <window> seconds, while the character-window stash API seems to reset the number of tracked requests every <window> seconds.

                Thoughts: Might be easier to just implement a request queue for each policy and only send 1 request from that queue every <limit>/<window> + .0X seconds to force observence of the rate limit wihtout having to do a ton of tracking... Will cost performance in
                    in cases where multiple tabs need to be updated upon zoning though.

                    For now, just track the requests made in the last <window> seconds, and when a response is processed, only keep the number of requests reported in <state>
            
        
        Rate limiter is implemented in such a way that each time you are going to query an API endpoint, you first ask the rate limiter if you have reached your limit for that type of request.
        It assumes that each API endpoint will use the same rate limit policy every time it is requested
        For POST requests, it assumes that the URL identifies the API endpoint.
        for GET requests, it assumes that the portion of the URL that is not programatically generated identifies the endpoint
            for example, https://www.pathofexile.com/api/trade/fetch/<item ID>,<item ID>,<item ID>,<item ID>,<item ID>,<item ID>,<item ID>,<item ID>,<item ID>,<item ID>?query=<query ID>
            is used to fetch results from trade searches, so https://www.pathofexile.com/api/trade/fetch/ would be treated as the endpoint for rate limit tracking,
            and https://www.pathofexile.com/character-window/get-stash-items would be used for stash tab requests
            
        It is possible that different API endpoints reuse the same policy, or will in the future. Therefore we check the rate limit based on endpoint->policy->rules->state
        
        ***This module can still get you locked out of an API endpoint if other programs are hitting the endpoint (you are doing manual searches in your browser), or if you create race conditions
        by hitting endpoints from more than 1 thread without semaphore locks around each checkRateLimit and processResponse pair"""


    #TODO: Update this class to gracefully handle being locked out

    def __init__(self):
        self.endpoints = {} #maps API endpoints to the policies they use
        self.policies = {} #stores info on the rate limits and current state of each policy
        self.policyMaxAges = {} #stores the max age that any request will need to be tracked for under this policy. i.e. the rule with the highest window is the max age.
        self.requestLog = {} #logs all requests to each policy. Keys are the policy names, values are lists of times.

    def checkRateLimit(self, endpoint):
        #returns True if the API endpoint is clear to make a request, False if the endpoint is about to be limited and should wait

        self.updateWindows()

        #if we have not seen this endpoint before, assume that we are not about to break the rate limit
        if not endpoint in self.endpoints:
            return True

        policy = self.endpoints[endpoint]
        rules = self.policies[policy]

        for rule in rules.values():
            for condition in rule:
                if condition["state"] >= condition["limit"] - 1:
                    return False

        print(self.policies)

        return True

    def processResponse(self, endpoint, headers):
        policy = headers['x-rate-limit-policy']

        if not endpoint in self.endpoints:
            self.endpoints[endpoint] = policy

        rules = headers['x-rate-limit-rules'].lower().split(",")

        if not policy in self.policies:
            self.policies[policy] = {}
            self.policyMaxAges[policy] = 0

        for rule in rules:
            ruleLimit = "x-rate-limit-"+rule
            ruleState = "x-rate-limit-"+rule+"-state"
            limitConditions = headers[ruleLimit].split(",")
            stateConditions = headers[ruleState].split(",")

            if not rule in self.policies[policy]:
                self.policies[policy][rule] = []
                for _ in limitConditions: #TODO: modify this later to catch a case where more conditions get added after the rule is initialized
                    self.policies[policy][rule].append({"limit":0,"state":0})

            for c in range(len(limitConditions)):
                limit = int(limitConditions[c].split(":")[0])
                age = int(limitConditions[c].split(":")[1])
                state = int(stateConditions[c].split(":")[0])
                self.policies[policy][rule][c]["limit"] = limit
                self.policies[policy][rule][c]["state"] = state
                self.policies[policy][rule][c]["age"] = age
                if age > self.policyMaxAges[policy]:
                    self.policyMaxAges[policy] = age
        
        self.logRequest(policy)
        print(self.policies)

            
    def updateWindows(self):
        now = datetime.datetime.now()
        
        for policy in self.policyMaxAges:
            #for each policy, remove all requests that are older than the max age
            maxWindowStart = now - datetime.timedelta(seconds=self.policyMaxAges[policy])
            for requestTime in self.requestLog[policy]:
                if requestTime < maxWindowStart:
                    self.requestLog[policy].remove(requestTime)
            
            #then for every rule in the policy count the number of requests that match each condition window
            for rule in self.policies[policy]:
                for condition in self.policies[policy][rule]:
                    windowStart = now - datetime.timedelta(seconds=condition["age"])
                    state = 0
                    for requestTime in self.requestLog[policy]:#TODO: Change this to accomidate cases like the character window API that hard resets the number of tracked requests on a cycle.
                        if windowStart <= requestTime:
                            state += 1
                    condition["state"] = state

    def logRequest(self, policy):
        if not policy in self.requestLog:
            self.requestLog[policy] = []
        self.requestLog[policy].append(datetime.datetime.now())