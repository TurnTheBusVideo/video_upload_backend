const AWS = require('aws-sdk');

const lambda = new AWS.Lambda({
  region: 'ap-south-1',
  httpOptions: { timeout: 300000 },
});


export const invokeLambda = (params = {}, originalRequest: any): Promise<LambdaResponse> => {
  const finalParams = {
    InvocationType: 'RequestResponse',
    ...params,
  };
  logger.debug(`Invoking Lambda ${finalParams.FunctionName} with params ${JSON.stringify(finalParams)}`);

  return new Promise(((fulfill, reject) => {
    lambda.invoke(finalParams, (err, data) => {
      logger.debug('Lambda completed, data: ', data);
      if (err) {
        logger.error('Lambda completed, err: ', err);
      } else {
        fulfill(data);
      }
    });
  }));
};

module.exports = {
  invokeLambda
}
