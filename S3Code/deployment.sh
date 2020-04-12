zip -r lambdaFunc.zip .

aws lambda update-function-code --function-name uploadVideo --zip-file fileb://lambdaFunc.zip --region ap-south-1
