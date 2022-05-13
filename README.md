# Routriever
DRTrack API Interface
Routriever is used to pull down and parse routes from DRTrack to a CSV file that then can be used with SmartConnect to push the data into Microsoft Dynamics NAV.

**Config Template**
For security purposes all app parameters have been encapsulated in an external file. This section outlines each parameter to help you produce your own config file 
_Parameters_
1. Web Service Links: This is the WSDL link provided by DRTrack to access their webservice for your business
2. Key File: The file path to your key file holding your password encryption key
3. Web Service Username: The username for your web service login.
4. Application Name: The name of your app accessing the web service
5. Branches: A comma-separated list of DRTrack branches you want to pull
6. Test Output: (Optional) File path for your test file output. This file will be filled with the repsonse for the first route on the first branch. Mostly used for testing
7. Routes Output: File path for the CSV with all parsed routes
8. Info Output: (Optional) File path for info.txt containing last time run and basic testing info
9. Error Alert Email Address: The gmail address used to send errors about routing. Currently the only error this alerts for is malformed stops within routes
10. Error Receiving Email Address: The email address you want to send the error alert to.

Once you've replaced the placeholders in the template with your parameters, simply delete the 'template' from the file name and save it.

**Crypto.py**
All passwords must be encrypted using Crypto.py and a key file with the encryption key must be manually created and placed in the project folder.
This protects passwords used in your web service and emails from the public by encrypting them using the cryptography library.

_Using Crypto.py_
Open crypto in the IDE of your choice and uncomment the bottom segment of code. this will allow you to run crypto in the terminal and generate an encrytion key
You should save your encryption key in its own key.txt file
If you have multiple passwords to encrypt, crypto will allow you to enter the original encryption key for each new password so that only one key will have to be created.
DON'T FORGET: re-comment the code when you finish or else it will prompt when you run routriever. 
It is easiest to save an uncommented version for future use than to re-edit it everytime

