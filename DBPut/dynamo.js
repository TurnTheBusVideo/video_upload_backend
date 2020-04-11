const AWS = require('aws-sdk');
const ddb = new AWS.DynamoDB.DocumentClient();

const putIntoDynamo = async (TableName, data) => {
  return ddb.put({
    TableName: TableName,
    Item: data,
  }).promise();
};

module.exports = {
  putIntoDynamo
}
