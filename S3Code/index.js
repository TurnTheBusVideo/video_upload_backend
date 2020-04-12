const { getSignedUrl } = require('./getSignedUrl');

exports.handler =

  async (event) => {
    let responseCode = 200;
    console.log("request: " + JSON.stringify(event));

    if (event.headers) {
      console.log("Received headers: " + event.headers);
    }

    const uploadedFileName = event.queryStringParameters.key;
    const splitFileNameArry = uploadedFileName.split('.');
    const name = splitFileNameArry.shift();
    const fileExtension = splitFileNameArry.pop();
    const fileName = name + '_' + Date.now() + '.' + fileExtension;

    const signedURL = getSignedUrl(fileName, bucket);

    const responseBody = {
      signedURL: signedURL,
      fileName: fileName
    };

    const response = {
      statusCode: responseCode,
      body: JSON.stringify(responseBody),
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*'
      }
    };
    console.log("response: " + JSON.stringify(response))
    return response;
  };



