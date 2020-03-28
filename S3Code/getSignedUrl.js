const AWS = require('aws-sdk');

const s3 = new AWS.S3({
  accessKeyId: 'AKIAJDIDCWJIC5L6ABBA',
  secretAccessKey: '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'
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