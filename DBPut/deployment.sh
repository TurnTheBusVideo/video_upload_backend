zip -r lambdaFunc.zip .

aws lambda update-function-code --function-name updateVideoMetadata --zip-file fileb://lambdaFunc.zip --region ap-south-1
