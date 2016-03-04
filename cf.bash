cf-create() {
  aws cloudformation create-stack --stack-name CXAR-ATO-46111-ElwinCF-$1 --template-body file:///Users/x7qj/src/elwin/CF-elwin.json --tags "[{\"Key\": \"Owner\",\"Value\": \"ndrcttps@nordstrom.com\"},{\"Key\": \"CostCenter\", \"Value\": \"46111\"}]" --capabilities CAPABILITY_IAM
}
cf-delete() {
  aws cloudformation delete-stack --stack-name CXAR-ATO-46111-ElwinCF-$1
}
cf-info() {
  aws cloudformation describe-stacks --stack-name CXAR-ATO-46111-ElwinCF-$1
}
cf-events() {
  aws cloudformation describe-stack-events --stack-name CXAR-ATO-46111-ElwinCF-$1
}