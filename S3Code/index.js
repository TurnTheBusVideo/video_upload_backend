const { getSignedUrl } = require('./getSignedUrl');

exports.handler = 

async (event) => {
  let responseCode = 200;
  console.log("request: " + JSON.stringify(event));
  
  
  if (event.headers) {
      console.log("Received headers: " + event.headers);
  }


  const fileName = event.queryStringParameters.key;

  const signedURL = getSignedUrl(fileName);

  const responseBody = {
    signedURL: signedURL,
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



