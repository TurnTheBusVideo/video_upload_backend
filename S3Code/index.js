const { getSignedUrl } = require('./getSignedUrl');

exports.handler = 

async (event) => {
  let responseCode = 200;
  console.log("request: " + JSON.stringify(event));
  
  
  if (event.headers) {
      console.log("Received headers: " + event.headers);
  }


  const fileName = event.queryStringParameters.key;
  const bucket = event.queryStringParameters.bucket;

  bucket

  const signedURL = getSignedUrl(fileName, bucket);

  // const args = {
  //   BUCKET_NAME: bucket,
  //   OBJECT_KEY: fileName,
  //   TEMP_FILE: 'Temp_S3File.mp4',
  //   VIDEO_TITLE: 'Test',
  //   VIDEO_DESCRIPTION: 'Awesome',
  //   VIDEO_CHANNEL: 'UCWuYgDOn2z66ZnUNmCTP0ig',
  //   TAGS: ["S3", "Test"]
  // };

  // const result = await invokeWorkerLambda({
  //   FunctionName: 'S3toYoutube',
  //   Payload: JSON.stringify(args),
  // });

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



