const AWS = require('aws-sdk');
const fs = require('fs');

const configFile = fs.readFileSync('config.json');
const configObj = JSON.parse(configFile);
const moderators = configObj['mods']; //array of mod emails

const cognitoIDP = new AWS.CognitoIdentityServiceProvider({
    accessKeyId: configObj.accessKeyId,
    secretAccessKey: configObj.secretAccessKey,
    region: 'ap-south-1'
});
const ses = new AWS.SES();

exports.handler = (event, context, callback) => {
    console.log('Version 🍫'); // for CloudWatch readability
    console.log('event details', JSON.stringify(event, null, 2));
    const { userName, userPoolId } = event;
    if (cognitoIDP && userName && userPoolId) {
        disableUser(userName, userPoolId, (status) => {
            console.log(status);
            callback(null, event);
        })
    }
    else {
        callback(null, event);
    }
};

const disableUser = (userName, userPoolId, callback) => {
    console.log(`===TRYING TO DISABLE USER ${userName}, ${userPoolId} ==`);
    var params = {
        UserPoolId: userPoolId,
        Username: userName
    };
    cognitoIDP.adminDisableUser(params, (err) => {
        if (err) {
            console.log(err);
            callback('⚠️ User not disabled, email not sent to moderators!');
        } else {
            console.log(" ✅ USER DISABLED ");
            sendEmail(moderators, userName, callback)
        }
    });
}

function sendEmail(to, userName, callback) {
    console.log("===TRYING TO MAIL MODERATORS===", to);
    var emailParams = {
        Destination: {
            ToAddresses: to
        },
        Message: {
            Body: {
                Text: {
                    Data:
                    `A new user (${userName}) has registered on the Turn the Bus video portal.
Their account is disabled until explicitly enabled.
As a moderator you're expected to review the new user and enable their account.
If you wish to enable this account, please login to the AWS console and navigate to
Cognito IDP > Manage User Pools > content_creators > Users and Groups > Username (${userName}) > Enable User
                    `
                }
            },
            Subject: {
                Data: "Turn the Bus | Video Upload Portal | New User"
            }
        },
        // Replace source_email with your SES validated email address
        Source: 'noreply@turnthebus.org'
    };

    ses.sendEmail(emailParams, function(err, data){
        if (err) {
            console.log(err);
            callback('⚠️ User Disabled, failed to send email to moderators!');
        } else {
            console.log("✅ EMAIL SENT");
            callback('✅ User Disabled, email sent to moderators.');
        }
    });
};
