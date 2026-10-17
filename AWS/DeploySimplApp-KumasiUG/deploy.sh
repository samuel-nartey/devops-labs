#!/usr/bin/env bash
# Deploys the Community Wall v2 stack, injects the stack outputs into the page, and uploads it.
# Usage: ./deploy.sh [stack-name] [region]
set -euo pipefail

STACK="${1:-community-wall-v2}"
REGION="${2:-eu-west-1}"
cd "$(dirname "$0")"

echo "1/4 Deploying CloudFormation stack ($STACK in $REGION)..."
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name "$STACK" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION"

out() {
  aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}

API_URL="$(out ApiUrl)"
COGNITO_DOMAIN="$(out CognitoDomainUrl)"
CLIENT_ID="$(out UserPoolClientId)"
BUCKET="$(out BucketName)"
DIST_ID="$(out DistributionId)"
SITE_URL="$(out SiteUrl)"

echo "2/4 Writing config into the page..."
sed -e "s|PASTE_API_URL|$API_URL|" \
    -e "s|PASTE_COGNITO_DOMAIN|$COGNITO_DOMAIN|" \
    -e "s|PASTE_CLIENT_ID|$CLIENT_ID|" \
    frontend/index.html > index.deploy.html

echo "3/4 Uploading to s3://$BUCKET ..."
aws s3 cp index.deploy.html "s3://$BUCKET/index.html" --content-type "text/html" --region "$REGION"

echo "4/4 Invalidating the CloudFront cache..."
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*" >/dev/null

rm -f index.deploy.html
echo
echo "Done. Open: $SITE_URL"
echo "Make yourself an admin after you sign up once:"
echo "  aws cognito-idp admin-add-user-to-group --user-pool-id $(out UserPoolId) --username YOUR_EMAIL --group-name admin --region $REGION"
