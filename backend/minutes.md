# Meeting minutes 

17/3/2020
* Merge request resolved. The specs for iteration 2 is up.
* Decided to use json to store data instead of pickle
* 32 functions to be implemented. 
* one data file for users, one data file for channel, 
* implementing a check_valid_token function is the way to check when the user is logging in
* auth/register function can call auth/login function to output a token.
* have a file that contains get_user(), get_channel(), create_user(), ...
* need to fix the assumption.md
* standup implementation. store the message_id during the standup period into a separate data file. then call get_message() to grab all the messages. 
* in tests section, need to create some blackbox tests for the server/websites.
* requests vs urllib for the blackbox testing. 


---
* Osama: other, auth
* Cooper: channel, standups
* Leo: message, standups
* Wing: channels, user

---