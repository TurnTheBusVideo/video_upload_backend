const AWS = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();




const scanTable = (tableName) => {
  return new Promise(((fulfill, reject) => {
    console.log(`Scanning item from table ${tableName}`);

    ddb.scan({
      TableName: tableName,
      Select: 'ALL_ATTRIBUTES',
      ConsistentRead : false,
    }, (err, data) => {
      logger.debug('In dynamo return function');
      if (err) {
        logger.debug('Error in scanTable', err);
        reject(err);
      }
      fulfill(data);
    });
  }));
};

module.exports = {
  scanTable
}