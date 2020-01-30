zip -r lambdaFunc.zip .

aws lambda update-function-code --function-name uploadVideo --z
ip-file fileb://~/Desktop/lambda-code/lambdaFunc.zip --region ap-south-1