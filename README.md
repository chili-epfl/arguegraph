# ArgueGraph

This repository contains files that can be used to run ArgueGraph in combination with Google Forms and Google Spreadsheets. 

You could also configure the setup with different questions or different data collection methods based on your own needs.

## Preparation

### Questionnaires

1. Create two Google forms for the pre- and post- questionnaires.

2. Questions can be found from the function `calculate_distances` in [util.py](https://github.com/chili-epfl/arguegraph/blob/main/util.py). You can find answers for each question in the same file.

3. Two questionnaires are identical but should be linked to two different Google spreadsheets, storing the responses.

4. Modify the Google form settings to collect their email addresses automatically. In this way, there will be an `Email address` field in the response spreadsheets, which is aligned with the code in [util.py](https://github.com/chili-epfl/arguegraph/blob/main/util.py).

5. Publish the forms, and update the polls' links in [arguegraph.ipynb](https://github.com/chili-epfl/arguegraph/blob/main/arguegraph.ipynb)

### service_account.json 

1. Create the Service Account & Get the Key

- Go to [Google Cloud Console](console.cloud.google.com).

- Create a project, e.g., "ArgueGraph Project".

- Enable the APIs for both Google Sheets and Google Drive:
    - Go to the "APIs & Services" Dashboard.
    - Click "ENABLE APIS AND SERVICES".
    - Search for and enable the "Google Sheets API".
    - Search for and enable the "Google Drive API" (this is needed by *gspread* package to find the sheets by their URLs).

- Create Service Account Credentials:
    - In the sidebar, go to "IAM & Admin" > "Service Accounts".
    - Click "CREATE SERVICE ACCOUNT".
    - Give it a name (e.g., "sheets-notebook-bot"). Click "Create and Continue".
    - Skip the roles (Step 2). Click "Continue".
    - Skip "Grant users access" (Step 3). Click "Done".

- Generate the JSON Key:
    - Click the three-dot menu (⋮) under the "Actions" column.
    - Select "Manage keys".
    - Click "ADD KEY" > "Create new key".
    - Select the key type JSON and click "Create".
    - Your browser will download a file. Rename this file to `service_account.json`. 

2. Share Your Google Sheets with the Service Account

- Open the `service_account.json` file with a text editor.

- Find the line that says "client_email" and copy the email address. For example: `"client_email": "sheets-notebook-bot@your-project-name.iam.gserviceaccount.com"`

- Go to your Google Spreadsheets (the ones for PRE_INPERSON_URL, POST_INPERSON_URL, etc.) and click the "Share" button in the top-right corner.

- Paste the service account's email address into the "Add people" box and give it "Editor" access.

3. Place the File and Run Your Code

- Put the `service_account.json` file in the directory containing [arguegraph.ipynb](https://github.com/chili-epfl/arguegraph/blob/main/arguegraph.ipynb)

- Make sure you have the required libraries installed. If not, run the command below in the terminal:
    ```
    pip install -r requirements.txt
    ```

**[Important Security Note] service_account.json is like a private key that grants access to your sheets. DO NOT share it publicly.**

### Update the links

Once you've done everything above, the last step is to update the spreadsheet links in [util.py](https://github.com/chili-epfl/arguegraph/blob/main/util.py), and the questionnaire links in [arguegraph.ipynb](https://github.com/chili-epfl/arguegraph/blob/main/arguegraph.ipynb).

Then just follow the notebook struture to run the activity, for example:

1. Distribute the pre-questionnaire to students and ask them to answer the quetsions

2. Run the analysis and show the results with all pairs

3. Allot some time for argumentation and encourage them to convince their partners

4. Distribute the post-questionnaire to students and ask them to answer the same questions again

5. Run the analysis and show the plot comparing the differences among all pairs

6. Debrief the activity

## References
```
Jermann, P., & Dillenbourg, P. (2003). Elaborating new arguments through a CSCL script. In Arguing to learn: Confronting cognitions in computer-supported collaborative learning environments (pp. 205-226). Dordrecht: Springer Netherlands.

Jermann, P., & Dillenbourg, P. (1999). An analysis of learner arguments in a collective learning environment. In Third CSCL Conference (pp. 265-273).
```