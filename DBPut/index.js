const { putIntoDynamo } = require('./dynamo');

exports.handler =

  async (event) => {
    let responseCode = 200;
    console.log("request: " + JSON.stringify(event));

    if (event.headers) {
      console.log("Received headers: " + event.headers);
    }
    const fileName = event.queryStringParameters.key;

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

    const tagsString = tags && typeof tags === 'string' ? tags : "Turn the bus, educational, tutorial, tutor, education";
    const trimmedTagsArray = tagsString.split(',').map(word => word.trim());

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
      Tags: trimmedTagsArray
    };

    console.log('Writing to DB', JSON.stringify(data));

    await putIntoDynamo('UploadVideo', data);

    console.log('DB write successful', JSON.stringify(data));
    
    const response = {
      statusCode: responseCode,
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*'
      }
    };
    console.log("response: " + JSON.stringify(response))
    return response;
  };



