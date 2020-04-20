const AWS = require('aws-sdk');
const fs = require('fs');


let rawConfig = fs.readFileSync('config.json');
let jsonConfig = JSON.parse(rawConfig);

const cognitoIDP = new AWS.CognitoIdentityServiceProvider({
    accessKeyId: jsonConfig.accessKeyId,
    secretAccessKey: jsonConfig.secretAccessKey,
    region: 'ap-south-1'
});


exports.handler = (event, context, callback) => {
    console.log('event details', JSON.stringify(event, null, 2));
    const { userName, userPoolId } = event;
    if (cognitoIDP && userName && userPoolId) {
        disableUser(userName, userPoolId, (status) => {
            callback(null, event);
        })
    }
    else {
        callback(null, event);
    }
};

const disableUser = (userName, userPoolId, wrappedCallback) => {
    console.log(`Trying to disable user: ${userName}, ${userPoolId}`);
    var params = {
        UserPoolId: userPoolId,
        Username: userName
    };
    cognitoIDP.adminDisableUser(params, (err) => {
        if (err) {
            console.log(err);
        } else {
            console.log("===USER DISABLED===");
        }
        wrappedCallback('User Disabled');
    });
}
