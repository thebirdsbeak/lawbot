signatories={
				"nda": ["Craig", "Anoop", "Flaviana"],
    			"partner": ["Graeme", "Catherine", "Andrew"],
    			"freelance":  ["Martin", "Dabo", "Robert"]
			}


# need to account for different signing entities. Should we also have a function here that takes
# an entity and document type and returns the answer
# bonus points if we can return the actual user in slack ie user = slack_client.user.profile.get('[email_address]') and also their status 
# so we can explain if they are available user.status_text and/ or user.status_emoji
# we can also handle if users are deleted or no longer active here 

greetings = ["hello","hi","hey", "yo", "greetings","sup","hiya",
             "salutations", "howdy", "howdy-doody", "bonjour",
             "morning", "good day", "good morning", "buenas dias",
             "buenas noches"]
