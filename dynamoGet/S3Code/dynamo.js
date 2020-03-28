const AWS = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();

const getFromDynamo = async (TableName, data) => {
  return ddb.batchGet({ TableName: TableName }).promise();
};

module.exports = {
  putIntoDynamo
}
