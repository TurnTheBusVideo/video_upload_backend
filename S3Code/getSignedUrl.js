const AWS = require('aws-sdk');

const s3 = new AWS.S3({
  accessKeyId: '...',
  secretAccessKey: '...'
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