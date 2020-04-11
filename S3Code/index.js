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

    const {
      bucket,
      classN,
      stream,
      board,
      bookName,
      bookPartName,
      chapterName,
      chapterNumber,
      chapterPart,
      section,
      tags,
      title,
      description,
      videoLanguage,
      awsRegion
    } = event.queryStringParameters;

    const signedURL = getSignedUrl(fileName, bucket);

    const data = {
      fileName,
      uploadID: fileName,
      AWS_REGION: awsRegion,
      s3URL: `https://${bucket}.s3.amazonaws.com/${fileName}`,
      Bucket: bucket,
      classN,
      stream,
      board,
      bookName,
      bookPartName,
      chapterName,
      chapterNumber,
      chapterPart,
      section,
      videoTitle: title,
      videoDescription: description,
      videoLanguage,
      Tags: tags.split(',')
    };

    console.log(JSON.stringify(data));


    // const args = {
    //   BUCKET_NAME: bucket,
    //   OBJECT_KEY: fileName,
    //   TEMP_FILE: 'Temp_S3File.mp4',
    //   VIDEO_TITLE: 'Test',
    //   VIDEO_DESCRIPTION: 'Awesome',
    //   VIDEO_CHANNEL: 'UCWuYgDOn2z66ZnUNmCTP0ig',
    //   TAGS: ["S3", "Test"]
    // };

    // const result = await invokeLambda({
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



