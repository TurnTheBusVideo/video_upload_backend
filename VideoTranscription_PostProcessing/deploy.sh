FILE=lambdaFunc.zip
if test -f "$FILE"; then
    rm -rf lambdaFunc.zip
fi

zip -r lambdaFunc.zip lambda_function.py

aws lambda update-function-code --function-name VideoTranscription_PostProcessing --zip-file fileb://lambdaFunc.zip --region ap-south-1
