cf-create() {
  aws cloudformation create-stack --stack-name CXAR-ATO-46111-ElwinCF --template-body file:///Users/x7qj/src/elwin/CF-elwin.json --tags "[{\"Key\": \"Owner\",\"Value\": \"ndrcttps@nordstrom.com\"},{\"Key\": \"CostCenter\", \"Value\": \"46111\"}]" --capabilities CAPABILITY_IAM
}
cf-delete() {
  aws cloudformation delete-stack --stack-name CXAR-ATO-46111-ElwinCF
}