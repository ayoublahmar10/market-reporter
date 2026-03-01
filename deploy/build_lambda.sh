#!/bin/bash
# Run this script in AWS CloudShell to build the Lambda deployment package.
# AWS CloudShell is already Linux x86_64 — no platform flags needed.
#
# Steps:
#   1. Open AWS Console → CloudShell (top bar icon)
#   2. Upload your project zip: Actions → Upload file
#   3. Run: unzip market-reporter.zip && cd market-reporter && bash deploy/build_lambda.sh
#   4. Download the generated lambda_package.zip: Actions → Download file

set -e

PACKAGE_DIR="lambda_package"
OUTPUT_ZIP="lambda_package.zip"

echo "=== Building Lambda deployment package ==="

# Fix line endings in case the script was edited on Windows
sed -i 's/\r//' requirements.txt

# Clean previous build
rm -rf "$PACKAGE_DIR" "$OUTPUT_ZIP"
mkdir "$PACKAGE_DIR"

# Install all dependencies directly (CloudShell is already Linux x86_64)
pip install -r requirements.txt --target "$PACKAGE_DIR" --upgrade --quiet

# Copy source files into the package
cp *.py "$PACKAGE_DIR/"
cp -r collectors/ "$PACKAGE_DIR/collectors/"

# Zip everything (exclude bytecode and cache)
cd "$PACKAGE_DIR"
zip -r "../$OUTPUT_ZIP" . -x "*.pyc" -x "*/__pycache__/*"
cd ..

echo ""
echo "✓ Package ready: $OUTPUT_ZIP ($(du -sh $OUTPUT_ZIP | cut -f1))"
echo "  → Download it with: Actions → Download file → lambda_package.zip"
