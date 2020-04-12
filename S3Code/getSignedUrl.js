const AWS = require('aws-sdk');
const fs = require('fs');

let rawConfig = fs.readFileSync('config.json');
let jsonConfig = JSON.parse(rawConfig);

const s3 = new AWS.S3({
  accessKeyId: jsonConfig.accessKeyId,
  secretAccessKey: jsonConfig.secretAccessKey
});

const getSignedUrl = (fileName, bucketName) => {
  const params = {
    Bucket: bucketName,
    Key: fileName
  };
  return s3.getSignedUrl('putObject', params);
}

module.exports = {
  getSignedUrl
};